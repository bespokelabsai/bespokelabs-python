"""Results of checking claims against shared context with Nimble."""

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel
from .nimble.system_one_response import Usage

Effort = Literal["low", "medium", "high"]


class FactcheckResult(BaseModel):
    claim: str
    support_prob: float
    """Nimble's probability that the context supports the entire claim."""


class FactcheckResponse(BaseModel):
    results: List[FactcheckResult]
    """One result per input claim, in the same order, including duplicates."""

    model: str
    usage: Usage
    request_id: Optional[str] = None
