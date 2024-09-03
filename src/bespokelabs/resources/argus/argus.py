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

__all__ = ["ArgusResource", "AsyncArgusResource"]


class ArgusResource(SyncAPIResource):
    @cached_property
    def factcheck(self) -> FactcheckResource:
        return FactcheckResource(self._client)

    @cached_property
    def with_raw_response(self) -> ArgusResourceWithRawResponse:
        return ArgusResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ArgusResourceWithStreamingResponse:
        return ArgusResourceWithStreamingResponse(self)


class AsyncArgusResource(AsyncAPIResource):
    @cached_property
    def factcheck(self) -> AsyncFactcheckResource:
        return AsyncFactcheckResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncArgusResourceWithRawResponse:
        return AsyncArgusResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncArgusResourceWithStreamingResponse:
        return AsyncArgusResourceWithStreamingResponse(self)


class ArgusResourceWithRawResponse:
    def __init__(self, argus: ArgusResource) -> None:
        self._argus = argus

    @cached_property
    def factcheck(self) -> FactcheckResourceWithRawResponse:
        return FactcheckResourceWithRawResponse(self._argus.factcheck)


class AsyncArgusResourceWithRawResponse:
    def __init__(self, argus: AsyncArgusResource) -> None:
        self._argus = argus

    @cached_property
    def factcheck(self) -> AsyncFactcheckResourceWithRawResponse:
        return AsyncFactcheckResourceWithRawResponse(self._argus.factcheck)


class ArgusResourceWithStreamingResponse:
    def __init__(self, argus: ArgusResource) -> None:
        self._argus = argus

    @cached_property
    def factcheck(self) -> FactcheckResourceWithStreamingResponse:
        return FactcheckResourceWithStreamingResponse(self._argus.factcheck)


class AsyncArgusResourceWithStreamingResponse:
    def __init__(self, argus: AsyncArgusResource) -> None:
        self._argus = argus

    @cached_property
    def factcheck(self) -> AsyncFactcheckResourceWithStreamingResponse:
        return AsyncFactcheckResourceWithStreamingResponse(self._argus.factcheck)
