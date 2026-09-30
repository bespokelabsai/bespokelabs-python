"""Nimble resource using the shared Bespoke Labs transport and authentication."""

from __future__ import annotations

from typing import Mapping, cast
from functools import partial

import httpx

from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import (
    is_mapping,
    maybe_transform,
    async_maybe_transform,
)
from .._compat import cached_property
from .._codegrep import CODEGREP_MODELS, parse_codegrep, prepare_codegrep
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.nimble import system_one_params
from ..types.factcheck_response import Effort
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
        questions: Mapping[str, Question],
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

          questions: Named question dictionaries. Codegrep supports noul/boolean questions.

          model: Hosted model name or alias, including nimble-codegrep-low/medium/high.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        overrides: Mapping[str, object] = extra_body if is_mapping(extra_body) else {}
        selected_model = overrides.get("model", model)
        if isinstance(selected_model, str) and selected_model.startswith("nimble-codegrep"):
            if selected_model not in CODEGREP_MODELS:
                raise ValueError("Unknown Codegrep model; use nimble-codegrep-low, -medium, or -high")
            body = prepare_codegrep(
                state=overrides.get("state", state),
                questions=overrides.get("questions", questions),
                effort=cast(Effort, CODEGREP_MODELS[selected_model]),
            )
            body.pop("effort")
            body["model"] = selected_model
            return cast(
                SystemOneResponse,
                self._post(
                    "/v1/nimble/systemone",
                    body=body,
                    cast_to=object,
                    options=make_request_options(
                        extra_headers=extra_headers,
                        extra_query=extra_query,
                        extra_body=extra_body,
                        timeout=timeout,
                        post_parser=partial(parse_codegrep, question_ids=list(body["questions"])),
                    ),
                ),
            )
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
        questions: Mapping[str, Question],
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

          questions: Named question dictionaries. Codegrep supports noul/boolean questions.

          model: Hosted model name or alias, including nimble-codegrep-low/medium/high.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        overrides: Mapping[str, object] = extra_body if is_mapping(extra_body) else {}
        selected_model = overrides.get("model", model)
        if isinstance(selected_model, str) and selected_model.startswith("nimble-codegrep"):
            if selected_model not in CODEGREP_MODELS:
                raise ValueError("Unknown Codegrep model; use nimble-codegrep-low, -medium, or -high")
            body = prepare_codegrep(
                state=overrides.get("state", state),
                questions=overrides.get("questions", questions),
                effort=cast(Effort, CODEGREP_MODELS[selected_model]),
            )
            body.pop("effort")
            body["model"] = selected_model
            return cast(
                SystemOneResponse,
                await self._post(
                    "/v1/nimble/systemone",
                    body=body,
                    cast_to=object,
                    options=make_request_options(
                        extra_headers=extra_headers,
                        extra_query=extra_query,
                        extra_body=extra_body,
                        timeout=timeout,
                        post_parser=partial(parse_codegrep, question_ids=list(body["questions"])),
                    ),
                ),
            )
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
