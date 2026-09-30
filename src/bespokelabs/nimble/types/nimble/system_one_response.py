"""Typed results from Nimble's candidate scoring service."""

from typing import Dict, Union, Optional
from typing_extensions import Literal, Annotated

from pydantic import Field

from ..._utils import PropertyInfo
from ..._models import BaseModel

__all__ = ["NoulAnswer", "ChoiceAnswer", "ScoreAnswer", "Answer", "Usage", "SystemOneResponse", "CodegrepDetail"]


class NoulAnswer(BaseModel):
    type: Literal["noul"]
    noul: float
    """Score for true; Codegrep models return calibrated relevance."""


class ChoiceAnswer(BaseModel):
    type: Literal["choice"]
    choice: str
    probabilities: Dict[str, float]
    confidence: float
    """Distribution concentration, not calibrated correctness."""


class ScoreAnswer(BaseModel):
    type: Literal["score"]
    score: float
    """Expected zero-based rubric index, not a probability."""
    legend: Dict[str, str]
    probabilities: Dict[str, float]
    confidence: float


Answer = Annotated[Union[NoulAnswer, ChoiceAnswer, ScoreAnswer], PropertyInfo(discriminator="type")]


class Usage(BaseModel):
    input_tokens: int
    output_tokens: int


class CodegrepDetail(BaseModel):
    raw: Optional[float]
    """Uncalibrated probability; None when the item was too long to score."""
    overflow: bool
    escalated: bool
    scores: Dict[str, Optional[float]]
    """Raw probabilities for the models that evaluated this question."""


class SystemOneResponse(BaseModel):
    model: str
    answers: Dict[str, Answer]
    usage: Usage
    request_id: Optional[str] = None
    details: Dict[str, CodegrepDetail] = Field(default_factory=dict)
    """Per-question metadata when the selected model is Codegrep."""
    escalation_skipped: bool = False
    """Whether Codegrep medium returned its smaller model fallback."""

    @property
    def nouls(self) -> Dict[str, NoulAnswer]:
        return {name: answer for name, answer in self.answers.items() if isinstance(answer, NoulAnswer)}

    @property
    def choices(self) -> Dict[str, ChoiceAnswer]:
        return {name: answer for name, answer in self.answers.items() if isinstance(answer, ChoiceAnswer)}

    @property
    def scores(self) -> Dict[str, ScoreAnswer]:
        return {name: answer for name, answer in self.answers.items() if isinstance(answer, ScoreAnswer)}
