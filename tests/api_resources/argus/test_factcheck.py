# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from bespokelabs import Bespokelabs, AsyncBespokelabs
from tests.utils import assert_matches_type
from bespokelabs.types.argus import FactcheckCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestFactcheck:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Bespokelabs) -> None:
        factcheck = client.argus.factcheck.create(
            claim="claim",
            contexts=["string", "string", "string"],
        )
        assert_matches_type(FactcheckCreateResponse, factcheck, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Bespokelabs) -> None:
        response = client.argus.factcheck.with_raw_response.create(
            claim="claim",
            contexts=["string", "string", "string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        factcheck = response.parse()
        assert_matches_type(FactcheckCreateResponse, factcheck, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Bespokelabs) -> None:
        with client.argus.factcheck.with_streaming_response.create(
            claim="claim",
            contexts=["string", "string", "string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            factcheck = response.parse()
            assert_matches_type(FactcheckCreateResponse, factcheck, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncFactcheck:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncBespokelabs) -> None:
        factcheck = await async_client.argus.factcheck.create(
            claim="claim",
            contexts=["string", "string", "string"],
        )
        assert_matches_type(FactcheckCreateResponse, factcheck, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncBespokelabs) -> None:
        response = await async_client.argus.factcheck.with_raw_response.create(
            claim="claim",
            contexts=["string", "string", "string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        factcheck = await response.parse()
        assert_matches_type(FactcheckCreateResponse, factcheck, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncBespokelabs) -> None:
        async with async_client.argus.factcheck.with_streaming_response.create(
            claim="claim",
            contexts=["string", "string", "string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            factcheck = await response.parse()
            assert_matches_type(FactcheckCreateResponse, factcheck, path=["response"])

        assert cast(Any, response.is_closed) is True
