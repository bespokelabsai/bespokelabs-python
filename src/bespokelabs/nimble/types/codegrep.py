"""Parameters and results for code relevance scoring."""

from __future__ import annotations

from typing import Any, Dict, Union

from .nimble.system_one_params import NoulQuestion, BooleanQuestion
from .nimble.system_one_response import (
    CodegrepDetail as CodegrepDetail,
    SystemOneResponse,
)

CodegrepState = Union[str, Dict[str, Any]]


CodegrepQuestion = Union[NoulQuestion, BooleanQuestion]

CodegrepResponse = SystemOneResponse
