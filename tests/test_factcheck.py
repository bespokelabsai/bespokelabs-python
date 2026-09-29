from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from bespokelabs import nimble
from bespokelabs.nimble.types import FactcheckResponse


@pytest.mark.parametrize("count", [1, 3, 64])
@pytest.mark.parametrize("use_async", [False, True])
async def test_factcheck_batch(count: int, use_async: bool) -> None:
    # Duplicate claims and reverse answer order detect ordering/data-loss bugs.
    claims = ["The sky is blue."] * count
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        assert request.url.path == "/v1/nimble/systemone"
        assert request.headers["api_key"] == "test"
        assert request.headers["x-custom"] == "value"
        assert request.url.params["trace"] == "1"
        assert request.extensions["timeout"]["read"] == 7
        body = json.loads(request.content)
        assert body["state"] == "Today the sky is blue."
        assert body["model"] == "custom-model"
        questions = body["questions"]
        assert len(questions) == count
        for index, claim in enumerate(claims):
            question = questions[str(index)]
            assert question["type"] == "noul"
            assert question["instructions"]["claim"] == claim
            assert set(question["criteria"]) == {"true", "false"}
        return httpx.Response(
            200,
            json={
                "model": "custom-model",
                "answers": {str(i): {"type": "noul", "noul": i / count} for i in reversed(range(count))},
                "usage": {"input_tokens": 100, "output_tokens": count},
                "request_id": "request-test",
            },
        )

    kwargs: Any = dict(
        context="Today the sky is blue.",
        claims=claims,
        model="custom-model",
        extra_headers={"x-custom": "value"},
        extra_query={"trace": "1"},
        timeout=7,
    )
    if use_async:
        async with nimble.AsyncNimble(
            api_key="test", http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler))
        ) as client:
            result = await client.with_options(max_retries=0).factcheck(**kwargs)
    else:
        with nimble.Nimble(
            api_key="test", http_client=httpx.Client(transport=httpx.MockTransport(handler))
        ) as sync_client:
            result = sync_client.with_options(max_retries=0).factcheck(**kwargs)
    assert len(seen) == 1
    assert isinstance(result, FactcheckResponse)
    assert [item.claim for item in result.results] == claims
    assert [item.support_prob for item in result.results] == [i / count for i in range(count)]
    assert result.model == "custom-model"
    assert result.request_id == "request-test"
    assert result.usage.input_tokens == 100
    assert result.usage.output_tokens == count


@pytest.mark.parametrize("use_async", [False, True])
@pytest.mark.parametrize(
    "overrides,error",
    [
        ({"claims": []}, ValueError),
        ({"claims": ["x"] * 65}, ValueError),
        ({"claims": "x"}, ValueError),
        ({"claims": [" "]}, ValueError),
        ({"claims": [42]}, ValueError),
        ({"context": " "}, ValueError),
        ({"context": None}, ValueError),
        ({"effort": "invalid"}, ValueError),
        ({"effort": "low"}, NotImplementedError),
        ({"effort": "high"}, NotImplementedError),
    ],
)
async def test_invalid_factcheck_does_not_send(
    use_async: bool, overrides: dict[str, Any], error: type[Exception]
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        pytest.fail(f"Unexpected request: {request.url}")

    kwargs: Any = {"context": "context", "claims": ["claim"], **overrides}
    if use_async:
        async with nimble.AsyncNimble(
            api_key="test", http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler))
        ) as client:
            with pytest.raises(error):
                await client.factcheck(**kwargs)
    else:
        with nimble.Nimble(
            api_key="test", http_client=httpx.Client(transport=httpx.MockTransport(handler))
        ) as sync_client:
            with pytest.raises(error):
                sync_client.factcheck(**kwargs)


@pytest.mark.parametrize(
    "answers",
    [
        {},
        {"0": {"type": "noul", "noul": 0.5}, "extra": {"type": "noul", "noul": 0.7}},
        {"0": {"type": "choice", "choice": "true", "probabilities": {}, "confidence": 1}},
        {"0": {"type": "noul", "noul": 2}},
        {"0": {"type": "noul", "noul": -1}},
        {"0": {"type": "noul"}},
    ],
)
def test_invalid_factcheck_response(answers: dict[str, Any]) -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "model": "nimble-latest",
                "answers": answers,
                "usage": {"input_tokens": 1, "output_tokens": 1},
            },
        )

    with nimble.Nimble(api_key="test", http_client=httpx.Client(transport=httpx.MockTransport(handler))) as client:
        with pytest.raises(ValueError, match="Invalid factcheck response"):
            client.factcheck(context="context", claims=["claim"], effort="medium")


def test_client_aliases() -> None:
    assert nimble.Nimble is nimble.BespokeLabs is nimble.Client
    assert nimble.AsyncNimble is nimble.AsyncBespokeLabs is nimble.AsyncClient
