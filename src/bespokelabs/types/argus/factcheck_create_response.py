# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ..._models import BaseModel

__all__ = ["FactcheckCreateResponse"]


class FactcheckCreateResponse(BaseModel):
    claim_supported_by_contexts: List[float]
