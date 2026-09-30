"""Parameters and results for code relevance scoring."""

from __future__ import annotations

from typing import Any, Dict, Union, Optional
from typing_extensions import Literal, Required, TypedDict

from .._models import BaseModel
from .nimble.system_one_params import Content
from .nimble.system_one_response import Usage, NoulAnswer

CodegrepState = Union[str, Dict[str, Any]]


class CodegrepQuestion(TypedDict, total=False):
    type: Required[Literal["noul", "boolean"]]
    instructions: Required[Content]
    criteria: Dict[Literal["true", "false"], str]


class CodegrepDetail(BaseModel):
    raw: Optional[float]
    """Uncalibrated probability; None when the item was too long to score."""
    overflow: bool
    escalated: bool
    scores: Dict[str, Optional[float]]
    """Raw probabilities for the models that evaluated this question."""


class CodegrepResponse(BaseModel):
    model: str
    answers: Dict[str, NoulAnswer]
    """Calibrated relevance scores, keyed by the original question IDs."""
    details: Dict[str, CodegrepDetail]
    usage: Usage
    """Service-reported usage, including additional model calls at medium effort."""
    escalation_skipped: bool
    """True when medium returned the smaller model's answers after fallback."""
    request_id: Optional[str] = None

    @property
    def nouls(self) -> Dict[str, NoulAnswer]:
        return self.answers
