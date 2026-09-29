"""Validate batched Factcheck requests and responses without coercing scores."""

from __future__ import annotations

import math
from typing import Any
from typing_extensions import TypeGuard

from ._utils import is_list, is_mapping
from ._models import validate_type
from .types.factcheck_response import Effort, FactcheckResponse


def prepare_factcheck(*, context: object, claims: object, effort: Effort, split_claims: bool = True) -> dict[str, Any]:
    if effort not in ("low", "medium", "high"):
        raise ValueError("effort must be 'low', 'medium', or 'high'")
    if not isinstance(context, str) or not context.strip() or len(context) > 400000:
        raise ValueError("context must contain 1 to 400000 characters and not be blank")
    if not is_list(claims) or not 1 <= len(claims) <= 64:
        raise ValueError("claims must be a list containing 1 to 64 strings")
    if any(not isinstance(claim, str) or not claim.strip() or len(claim) > 4000 for claim in claims):
        raise ValueError("each claim must contain 1 to 4000 characters and not be blank")
    if type(split_claims) is not bool:
        raise ValueError("split_claims must be a boolean")
    return {"context": context, "claims": list(claims), "effort": effort, "split_claims": split_claims}


def _probability(value: object) -> TypeGuard[float | int]:
    return not isinstance(value, bool) and isinstance(value, (float, int)) and 0 <= value <= 1 and math.isfinite(value)


def _count(value: object) -> bool:
    return not isinstance(value, bool) and isinstance(value, int) and 0 <= value <= 2**53 - 1


def parse_factcheck(*, claims: list[str], effort: Effort, response: object) -> FactcheckResponse:
    if not is_mapping(response) or response.get("effort") != effort:
        raise ValueError("Invalid factcheck response: unexpected effort")
    answers = response.get("results")
    if not is_list(answers) or len(answers) != len(claims):
        raise ValueError("Invalid factcheck response: expected exactly one result per claim")
    for claim, answer in zip(claims, answers):
        if not is_mapping(answer) or answer.get("claim") != claim:
            raise ValueError("Invalid factcheck response: invalid claim")
        prob = answer.get("support_prob")
        if not _probability(prob):
            raise ValueError("Invalid factcheck response: invalid probability")
        if type(answer.get("supported")) is not bool or answer["supported"] != (prob > 0.5):
            raise ValueError("Invalid factcheck response: invalid support decision")
        if "escalated" in answer and type(answer["escalated"]) is not bool:
            raise ValueError("Invalid factcheck response: invalid escalation status")
        if "scores" in answer:
            scores = answer["scores"]
            if not is_mapping(scores) or not scores or any(not _probability(v) for v in scores.values()):
                raise ValueError("Invalid factcheck response: invalid model scores")
    usage = response.get("usage")
    if not is_mapping(usage) or any(not _count(usage.get(key)) for key in ("input_tokens", "output_tokens")):
        raise ValueError("Invalid factcheck response: invalid usage")
    if type(response.get("escalation_skipped", False)) is not bool:
        raise ValueError("Invalid factcheck response: invalid escalation status")
    try:
        return validate_type(type_=FactcheckResponse, value=response)
    except ValueError as exc:
        raise ValueError("Invalid factcheck response: invalid metadata") from exc
