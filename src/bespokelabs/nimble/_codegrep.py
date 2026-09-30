"""Keep Codegrep's explicit state/question contract and validate its responses."""

from __future__ import annotations

import copy
from typing import Any

from ._utils import is_list, is_mapping
from ._models import validate_type
from ._factcheck import _count, _probability
from .types.codegrep import CodegrepResponse
from .types.factcheck_response import Effort


def prepare_codegrep(*, state: object, questions: object, effort: Effort) -> dict[str, Any]:
    if effort not in ("low", "medium", "high"):
        raise ValueError("effort must be 'low', 'medium', or 'high'")
    if not isinstance(state, str) and not is_mapping(state):
        raise ValueError("state must be a string or object")
    if isinstance(state, str) and not state.strip():
        raise ValueError("state must not be blank")
    if len(state if isinstance(state, str) else str(state)) > 2_000_000:
        raise ValueError("state must not exceed 2000000 characters")
    if not is_mapping(questions) or not 1 <= len(questions) <= 128:
        raise ValueError("questions must contain 1 to 128 named questions")
    for qid, question in questions.items():
        if not isinstance(qid, str) or not is_mapping(question):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise ValueError("questions must map string IDs to question objects")
        if set(question) - {"type", "instructions", "criteria"}:
            raise ValueError("unknown question field")
        if question.get("type") not in ("noul", "boolean"):
            raise ValueError("Codegrep supports only noul and boolean questions")
        instructions = question.get("instructions")
        if not (isinstance(instructions, str) or is_mapping(instructions) or is_list(instructions)):
            raise ValueError("instructions must be a string, object, or list")
        if isinstance(instructions, str) and not instructions.strip():
            raise ValueError("instructions must not be blank")
        criteria = question.get("criteria")
        if criteria is not None and (
            not is_mapping(criteria)
            or set(criteria) - {"true", "false"}
            or any(not isinstance(v, str) for v in criteria.values())
        ):
            raise ValueError("criteria must map true and false to strings")
    # Preserve caller IDs and snapshot nested data before an async request starts.
    return copy.deepcopy({"state": state, "questions": questions, "effort": effort})


def parse_codegrep(*, question_ids: list[str], response: object) -> CodegrepResponse:
    if not is_mapping(response):
        raise ValueError("Invalid Codegrep response")
    answers, details = response.get("answers"), response.get("details")
    if (
        not is_mapping(answers)
        or not is_mapping(details)
        or set(answers) != set(question_ids)
        or set(details) != set(question_ids)
    ):
        raise ValueError("Invalid Codegrep response: question IDs do not match")
    for qid in question_ids:
        answer, detail = answers[qid], details[qid]
        if not is_mapping(answer) or answer.get("type") != "noul" or not _probability(answer.get("noul")):
            raise ValueError("Invalid Codegrep response: invalid answer")
        if not is_mapping(detail) or any(type(detail.get(k)) is not bool for k in ("overflow", "escalated")):
            raise ValueError("Invalid Codegrep response: invalid details")
        raw = detail.get("raw")
        if "raw" not in detail or (raw is not None and not _probability(raw)):
            raise ValueError("Invalid Codegrep response: invalid raw score")
        if detail["overflow"]:
            if raw is not None or answer["noul"] != 1.0:
                raise ValueError("Invalid Codegrep response: invalid overflow answer")
        elif raw is None:
            raise ValueError("Invalid Codegrep response: missing raw score")
        scores = detail.get("scores")
        if not is_mapping(scores) or any(v is not None and not _probability(v) for v in scores.values()):
            raise ValueError("Invalid Codegrep response: invalid model scores")
    usage = response.get("usage")
    if not is_mapping(usage) or any(not _count(usage.get(k)) for k in ("input_tokens", "output_tokens")):
        raise ValueError("Invalid Codegrep response: invalid usage")
    if type(response.get("escalation_skipped")) is not bool:
        raise ValueError("Invalid Codegrep response: missing fallback status")
    try:
        return validate_type(type_=CodegrepResponse, value=response)
    except ValueError as error:
        raise ValueError("Invalid Codegrep response: invalid metadata") from error
