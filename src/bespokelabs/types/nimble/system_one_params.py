"""Parameters for the hosted Nimble API."""

from __future__ import annotations

from typing import Dict, List, Union
from typing_extensions import Literal, Required, TypedDict

__all__ = ["Content", "NoulQuestion", "ChoiceQuestion", "ScoreQuestion", "Question", "SystemOneParams"]

Content = Union[str, Dict[str, object], List[object]]


class NoulQuestion(TypedDict, total=False):
    type: Required[Literal["noul"]]
    instructions: Required[Content]
    criteria: Dict[Literal["true", "false"], str]
    """Optional descriptions for true and false."""


class ChoiceQuestion(TypedDict, total=False):
    type: Required[Literal["choice"]]
    instructions: Required[Content]
    criteria: Required[Dict[str, Union[str, None]]]
    """2–26 option keys mapped to descriptions, or None to use the key itself."""


class ScoreQuestion(TypedDict, total=False):
    type: Required[Literal["score"]]
    instructions: Required[Content]
    criteria: Required[List[str]]
    """2–26 ordered rubric descriptions, lowest first."""


Question = Union[NoulQuestion, ChoiceQuestion, ScoreQuestion]


class SystemOneParams(TypedDict, total=False):
    state: Required[Content]
    questions: Required[Dict[str, Question]]
    """1–64 questions keyed by caller-defined identifiers."""
    model: str
    """Defaults to nimble-latest."""
