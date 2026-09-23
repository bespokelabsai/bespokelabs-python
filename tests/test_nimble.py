from __future__ import annotations

import json
from typing import Any
from pathlib import Path

import httpx
import pytest

from bespokelabs import BespokeLabs, AsyncBespokeLabs, AuthenticationError, APIResponseValidationError
from bespokelabs.types.nimble import Question, NoulAnswer, ScoreAnswer, ChoiceAnswer

PAYLOAD = json.loads((Path(__file__).parent / "fixtures/nimble-systemone.json").read_text())
QUESTIONS: dict[str, Question] = {
    "refund": {"type": "noul", "instructions": "Does the customer request a refund?"},
    "department": {
        "type": "choice",
        "instructions": "Which department?",
        "criteria": {"billing": None, "technical": None},
    },
    "urgency": {
        "type": "score",
        "instructions": "Assess operational urgency.",
        "criteria": [
            "Routine billing request; service works",
            "Some functionality unavailable",
            "Complete service outage",
        ],
    },
}


def assert_answers(result: Any) -> None:
    assert isinstance(result.answers["refund"], NoulAnswer)
    assert isinstance(result.answers["department"], ChoiceAnswer)
    assert isinstance(result.answers["urgency"], ScoreAnswer)
    assert result.choices["department"].choice == "billing"
    assert result.nouls["refund"].noul > 0.99
    assert result.scores["urgency"].score == PAYLOAD["answers"]["urgency"]["score"]
    assert result.usage.output_tokens == 4


@pytest.mark.parametrize("strict", [False, True])
@pytest.mark.parametrize("surface", ["normal", "raw", "streaming", "client_raw", "client_streaming"])
def test_sync_nimble(strict: bool, surface: str, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BESPOKE_API_KEY", "bespoke-test")
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        assert request.method == "POST"
        assert str(request.url) == "https://gateway.example/v1/nimble/systemone"
        assert request.headers["api_key"] == "bespoke-test"
        assert "authorization" not in request.headers
        assert json.loads(request.content) == {
            "model": "nimble-latest",
            "state": {"text": "Refund please"},
            "questions": QUESTIONS,
        }
        return httpx.Response(200, json=PAYLOAD, headers={"x-request-id": "request-test"})

    with BespokeLabs(
        base_url="https://gateway.example",
        _strict_response_validation=strict,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    ) as client:
        resource = client.with_options(max_retries=0).nimble
        kwargs: Any = {"state": {"text": "Refund please"}, "questions": QUESTIONS}
        if surface == "normal":
            result = resource.system_one(**kwargs)
        elif surface in {"raw", "client_raw"}:
            target = resource.with_raw_response if surface == "raw" else client.with_raw_response.nimble
            raw = target.system_one(**kwargs)
            assert raw.headers["x-request-id"] == "request-test"
            result = raw.parse()
        else:
            target = (
                resource.with_streaming_response if surface == "streaming" else client.with_streaming_response.nimble
            )
            with target.system_one(**kwargs) as raw:
                result = raw.parse()
            assert raw.is_closed
        assert_answers(result)
    assert len(seen) == 1


@pytest.mark.parametrize("strict", [False, True])
@pytest.mark.parametrize("surface", ["normal", "raw", "streaming", "client_raw", "client_streaming"])
async def test_async_nimble(strict: bool, surface: str) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/nimble/systemone"
        assert request.headers["api_key"] == "bespoke-test"
        return httpx.Response(200, json=PAYLOAD)

    async with AsyncBespokeLabs(
        api_key="bespoke-test",
        _strict_response_validation=strict,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    ) as client:
        resource = client.with_options(max_retries=0).nimble
        kwargs: Any = {"state": "Refund please", "questions": QUESTIONS}
        if surface == "normal":
            result = await resource.system_one(**kwargs)
        elif surface in {"raw", "client_raw"}:
            target = resource.with_raw_response if surface == "raw" else client.with_raw_response.nimble
            result = await (await target.system_one(**kwargs)).parse()
        else:
            target = (
                resource.with_streaming_response if surface == "streaming" else client.with_streaming_response.nimble
            )
            async with target.system_one(**kwargs) as raw:
                result = await raw.parse()
            assert raw.is_closed
        assert_answers(result)


def test_minicheck_and_nimble_share_client() -> None:
    seen: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request.url.path)
        assert request.headers["api_key"] == "bespoke-test"
        return httpx.Response(200, json=PAYLOAD if "nimble" in request.url.path else {"support_prob": 0.9})

    with BespokeLabs(
        api_key="bespoke-test", http_client=httpx.Client(transport=httpx.MockTransport(handler))
    ) as client:
        assert client.minicheck.factcheck.create(claim="claim", context="context").support_prob == 0.9
        assert_answers(client.nimble.system_one(state="Refund", questions=QUESTIONS))
    assert seen == ["/v0/minicheck/factcheck", "/v1/nimble/systemone"]


def test_request_options_and_model_override() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["trace"] == "1"
        assert request.headers["x-custom"] == "value"
        body = json.loads(request.content)
        assert body["model"] == "bespokelabs/Bespoke-Nimble-9B"
        assert body["future"] is True
        assert request.extensions["timeout"]["read"] == 9.0
        return httpx.Response(200, json=PAYLOAD)

    with BespokeLabs(api_key="key", http_client=httpx.Client(transport=httpx.MockTransport(handler))) as client:
        client.nimble.system_one(
            state="text",
            questions=QUESTIONS,
            model="bespokelabs/Bespoke-Nimble-9B",
            extra_headers={"x-custom": "value"},
            extra_query={"trace": "1"},
            extra_body={"future": True},
            timeout=9.0,
        )


def test_existing_retry_and_authentication_errors() -> None:
    attempts: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        attempts.append(request)
        if len(attempts) == 1:
            return httpx.Response(529, json={"detail": "busy"}, headers={"retry-after-ms": "1"})
        return httpx.Response(401, json={"detail": "invalid key"})

    with BespokeLabs(api_key="key", http_client=httpx.Client(transport=httpx.MockTransport(handler))) as client:
        with pytest.raises(AuthenticationError):
            client.nimble.system_one(state="text", questions=QUESTIONS)
    assert len(attempts) == 2


def test_strict_response_validation() -> None:
    with BespokeLabs(
        api_key="key",
        _strict_response_validation=True,
        http_client=httpx.Client(transport=httpx.MockTransport(lambda _: httpx.Response(200, json={}))),
    ) as client:
        with pytest.raises(APIResponseValidationError):
            client.nimble.system_one(state="text", questions=QUESTIONS)
