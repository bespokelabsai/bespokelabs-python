"""Typed results from Nimble's candidate scoring service."""

from typing import Dict, Union, Optional
from typing_extensions import Literal, Annotated

from ..._utils import PropertyInfo
from ..._models import BaseModel

__all__ = ["NoulAnswer", "ChoiceAnswer", "ScoreAnswer", "Answer", "Usage", "SystemOneResponse"]


class NoulAnswer(BaseModel):
    type: Literal["noul"]
    noul: float
    """Probability of true, normalized over the two candidates."""


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


class SystemOneResponse(BaseModel):
    model: str
    answers: Dict[str, Answer]
    usage: Usage
    request_id: Optional[str] = None

    @property
    def nouls(self) -> Dict[str, NoulAnswer]:
        return {name: answer for name, answer in self.answers.items() if isinstance(answer, NoulAnswer)}

    @property
    def choices(self) -> Dict[str, ChoiceAnswer]:
        return {name: answer for name, answer in self.answers.items() if isinstance(answer, ChoiceAnswer)}

    @property
    def scores(self) -> Dict[str, ScoreAnswer]:
        return {name: answer for name, answer in self.answers.items() if isinstance(answer, ScoreAnswer)}
