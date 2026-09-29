"""Results of checking claims against shared context with Nimble."""

from typing import Dict, List, Optional
from typing_extensions import Literal

from .._models import BaseModel
from .nimble.system_one_response import Usage

Effort = Literal["low", "medium", "high"]


class FactcheckResult(BaseModel):
    claim: str
    support_prob: float
    """Nimble's probability that the context supports the entire claim."""

    supported: bool
    """Whether support_prob is greater than 0.5."""

    escalated: Optional[bool] = None
    """Whether this claim was checked by the tier's additional models."""

    scores: Optional[Dict[str, float]] = None
    """Per-model support probabilities when supplied by the selected tier."""


class FactcheckResponse(BaseModel):
    results: List[FactcheckResult]
    """One result per input claim, in the same order, including duplicates."""

    model: str
    effort: Effort
    escalation_skipped: bool = False
    usage: Usage
    request_id: Optional[str] = None
