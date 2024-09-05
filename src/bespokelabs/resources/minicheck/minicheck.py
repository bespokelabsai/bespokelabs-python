# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from ..._compat import cached_property
from .factcheck import (
    FactcheckResource,
    AsyncFactcheckResource,
    FactcheckResourceWithRawResponse,
    AsyncFactcheckResourceWithRawResponse,
    FactcheckResourceWithStreamingResponse,
    AsyncFactcheckResourceWithStreamingResponse,
)
from ..._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["MinicheckResource", "AsyncMinicheckResource"]


class MinicheckResource(SyncAPIResource):
    @cached_property
    def factcheck(self) -> FactcheckResource:
        return FactcheckResource(self._client)

    @cached_property
    def with_raw_response(self) -> MinicheckResourceWithRawResponse:
        return MinicheckResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> MinicheckResourceWithStreamingResponse:
        return MinicheckResourceWithStreamingResponse(self)


class AsyncMinicheckResource(AsyncAPIResource):
    @cached_property
    def factcheck(self) -> AsyncFactcheckResource:
        return AsyncFactcheckResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncMinicheckResourceWithRawResponse:
        return AsyncMinicheckResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncMinicheckResourceWithStreamingResponse:
        return AsyncMinicheckResourceWithStreamingResponse(self)


class MinicheckResourceWithRawResponse:
    def __init__(self, minicheck: MinicheckResource) -> None:
        self._minicheck = minicheck

    @cached_property
    def factcheck(self) -> FactcheckResourceWithRawResponse:
        return FactcheckResourceWithRawResponse(self._minicheck.factcheck)


class AsyncMinicheckResourceWithRawResponse:
    def __init__(self, minicheck: AsyncMinicheckResource) -> None:
        self._minicheck = minicheck

    @cached_property
    def factcheck(self) -> AsyncFactcheckResourceWithRawResponse:
        return AsyncFactcheckResourceWithRawResponse(self._minicheck.factcheck)


class MinicheckResourceWithStreamingResponse:
    def __init__(self, minicheck: MinicheckResource) -> None:
        self._minicheck = minicheck

    @cached_property
    def factcheck(self) -> FactcheckResourceWithStreamingResponse:
        return FactcheckResourceWithStreamingResponse(self._minicheck.factcheck)


class AsyncMinicheckResourceWithStreamingResponse:
    def __init__(self, minicheck: AsyncMinicheckResource) -> None:
        self._minicheck = minicheck

    @cached_property
    def factcheck(self) -> AsyncFactcheckResourceWithStreamingResponse:
        return AsyncFactcheckResourceWithStreamingResponse(self._minicheck.factcheck)
