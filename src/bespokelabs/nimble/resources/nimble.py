"""Nimble resource using the shared Bespoke Labs transport and authentication."""

from __future__ import annotations

import httpx

from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import (
    maybe_transform,
    async_maybe_transform,
)
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.nimble import system_one_params
from ..types.nimble.system_one_params import Content, Question
from ..types.nimble.system_one_response import SystemOneResponse

__all__ = ["NimbleResource", "AsyncNimbleResource"]


class NimbleResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> NimbleResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/bespokelabsai/bespokelabs-python#accessing-raw-response-data-eg-headers
        """
        return NimbleResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> NimbleResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/bespokelabsai/bespokelabs-python#with_streaming_response
        """
        return NimbleResourceWithStreamingResponse(self)

    def system_one(
        self,
        *,
        state: Content,
        questions: dict[str, Question],
        model: str = "nimble-latest",
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SystemOneResponse:
        """
        Evaluate typed Nimble questions against shared state.

        Args:
          state: Text, structured JSON, or a text transcript to evaluate.

          questions: Named Noul, Choice, or Score question dictionaries.

          model: Hosted model name or alias.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/nimble/systemone",
            body=maybe_transform(
                {
                    "state": state,
                    "questions": questions,
                    "model": model,
                },
                system_one_params.SystemOneParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SystemOneResponse,
        )


class AsyncNimbleResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncNimbleResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/bespokelabsai/bespokelabs-python#accessing-raw-response-data-eg-headers
        """
        return AsyncNimbleResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncNimbleResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/bespokelabsai/bespokelabs-python#with_streaming_response
        """
        return AsyncNimbleResourceWithStreamingResponse(self)

    async def system_one(
        self,
        *,
        state: Content,
        questions: dict[str, Question],
        model: str = "nimble-latest",
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SystemOneResponse:
        """
        Evaluate typed Nimble questions against shared state.

        Args:
          state: Text, structured JSON, or a text transcript to evaluate.

          questions: Named Noul, Choice, or Score question dictionaries.

          model: Hosted model name or alias.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/nimble/systemone",
            body=await async_maybe_transform(
                {
                    "state": state,
                    "questions": questions,
                    "model": model,
                },
                system_one_params.SystemOneParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SystemOneResponse,
        )


class NimbleResourceWithRawResponse:
    def __init__(self, nimble: NimbleResource) -> None:
        self._nimble = nimble

        self.system_one = to_raw_response_wrapper(
            nimble.system_one,
        )


class AsyncNimbleResourceWithRawResponse:
    def __init__(self, nimble: AsyncNimbleResource) -> None:
        self._nimble = nimble

        self.system_one = async_to_raw_response_wrapper(
            nimble.system_one,
        )


class NimbleResourceWithStreamingResponse:
    def __init__(self, nimble: NimbleResource) -> None:
        self._nimble = nimble

        self.system_one = to_streamed_response_wrapper(
            nimble.system_one,
        )


class AsyncNimbleResourceWithStreamingResponse:
    def __init__(self, nimble: AsyncNimbleResource) -> None:
        self._nimble = nimble

        self.system_one = async_to_streamed_response_wrapper(
            nimble.system_one,
        )
