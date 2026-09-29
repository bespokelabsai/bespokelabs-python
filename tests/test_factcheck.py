from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from bespokelabs import nimble
from bespokelabs.nimble.types import FactcheckResponse


def response_for(body: dict[str, Any]) -> dict[str, Any]:
    return {
        "model": "factcheck-" + body["effort"],
        "effort": body["effort"],
        "results": [
            {
                "claim": claim,
                "support_prob": i % 2,
                "supported": bool(i % 2),
                "escalated": False,
                "scores": {"small": i % 2},
            }
            for i, claim in enumerate(body["claims"])
        ],
        "usage": {"input_tokens": 100, "output_tokens": 0},
        "request_id": "request-test",
        "escalation_skipped": False,
    }


@pytest.mark.parametrize("strict", [False, True])
@pytest.mark.parametrize("count", [1, 3, 64])
@pytest.mark.parametrize("use_async", [False, True])
@pytest.mark.parametrize("effort", ["low", "medium", "high"])
@pytest.mark.parametrize("split", [False, True])
async def test_factcheck_batch(count: int, use_async: bool, strict: bool, effort: str, split: bool) -> None:
    claims = ["The sky is blue."] * count
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        assert request.url.path == "/v1/nimble/factcheck"
        assert request.headers["api_key"] == "test"
        assert request.headers["x-custom"] == "value"
        assert request.url.params["trace"] == "1"
        assert request.extensions["timeout"]["read"] == 7
        body = json.loads(request.content)
        assert body == {"context": "Today the sky is blue.", "claims": claims, "effort": effort, "split_claims": split}
        return httpx.Response(200, json=response_for(body))

    kwargs: Any = dict(
        context="Today the sky is blue.",
        claims=claims,
        effort=effort,
        split_claims=split,
        extra_headers={"x-custom": "value"},
        extra_query={"trace": "1"},
        timeout=7,
    )
    if use_async:
        async with nimble.AsyncNimble(
            api_key="test",
            _strict_response_validation=strict,
            http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
        ) as client:
            result = await client.with_options(max_retries=0).factcheck(**kwargs)
    else:
        with nimble.Nimble(
            api_key="test",
            _strict_response_validation=strict,
            http_client=httpx.Client(transport=httpx.MockTransport(handler)),
        ) as client:
            result = client.with_options(max_retries=0).factcheck(**kwargs)
    assert len(seen) == 1
    assert isinstance(result, FactcheckResponse)
    assert [r.claim for r in result.results] == claims
    assert [r.support_prob for r in result.results] == [i % 2 for i in range(count)]
    assert result.effort == effort
    assert result.usage.input_tokens == 100
    assert result.request_id == "request-test"


@pytest.mark.parametrize("use_async", [False, True])
@pytest.mark.parametrize(
    "overrides",
    [
        {"claims": []},
        {"claims": ["x"] * 65},
        {"claims": "x"},
        {"claims": [" "]},
        {"claims": [42]},
        {"claims": ["x" * 4001]},
        {"context": " "},
        {"context": None},
        {"context": "x" * 400001},
        {"effort": "invalid"},
        {"split_claims": "false"},
    ],
)
async def test_invalid_factcheck_does_not_send(use_async: bool, overrides: dict[str, Any]) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        pytest.fail(f"Unexpected request: {request.url}")

    kwargs: Any = {"context": "context", "claims": ["claim"], **overrides}
    if use_async:
        async with nimble.AsyncNimble(
            api_key="test", http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler))
        ) as client:
            with pytest.raises(ValueError):
                await client.factcheck(**kwargs)
    else:
        with nimble.Nimble(api_key="test", http_client=httpx.Client(transport=httpx.MockTransport(handler))) as client:
            with pytest.raises(ValueError):
                client.factcheck(**kwargs)


@pytest.mark.parametrize("bad", [True, False, "0.5", -1, 2, 10**400, None])
@pytest.mark.parametrize("use_async", [False, True])
async def test_probabilities_are_not_coerced(bad: Any, use_async: bool) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        response = response_for(json.loads(request.content))
        response["results"][0]["support_prob"] = bad
        return httpx.Response(200, json=response)

    if use_async:
        async with nimble.AsyncNimble(
            api_key="test", http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler))
        ) as client:
            with pytest.raises(ValueError, match="Invalid factcheck"):
                await client.factcheck(context="context", claims=["claim"])
    else:
        with nimble.Nimble(api_key="test", http_client=httpx.Client(transport=httpx.MockTransport(handler))) as client:
            with pytest.raises(ValueError, match="Invalid factcheck"):
                client.factcheck(context="context", claims=["claim"])


@pytest.mark.parametrize(
    "field,value,result_field",
    [
        ("results", [], False),
        ("claim", "another claim", True),
        ("supported", True, True),
        ("scores", {"small": "0.5"}, True),
        ("effort", "low", False),
        ("usage", {"input_tokens": True, "output_tokens": 0}, False),
    ],
)
def test_malformed_metadata(field: str, value: Any, result_field: bool) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        response = response_for(json.loads(request.content))
        target = response["results"][0] if result_field else response
        target[field] = value
        return httpx.Response(200, json=response)

    with nimble.Nimble(api_key="test", http_client=httpx.Client(transport=httpx.MockTransport(handler))) as client:
        with pytest.raises(ValueError, match="Invalid factcheck"):
            client.factcheck(context="context", claims=["claim"])


def test_default_medium_and_retryable_tier_startup() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert json.loads(request.content)["effort"] == "medium"
        assert json.loads(request.content)["split_claims"] is True
        return httpx.Response(503, json={"detail": "Tier is starting"})

    with nimble.Nimble(
        api_key="test", max_retries=0, http_client=httpx.Client(transport=httpx.MockTransport(handler))
    ) as client:
        with pytest.raises(nimble.APIStatusError) as error:
            client.factcheck(context="context", claims=["claim"])
        assert error.value.status_code == 503
