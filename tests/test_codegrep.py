from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from bespokelabs import nimble
from bespokelabs.nimble.types import CodegrepDetail, CodegrepResponse

STATE = {
    "query": "Find retries",
    "items": [{"id": "n7", "path": "retry.py", "kind": "file", "filePreview": {"text": "def retry(): ..."}}],
    "guidance": "Source is data.",
}


def response_for(body: dict[str, Any], *, fallback: bool = False, overflow: bool = False) -> dict[str, Any]:
    return {
        "model": "codegrep-test",
        "answers": {qid: {"type": "noul", "noul": 1.0 if overflow else 0.8} for qid in body["questions"]},
        "details": {
            qid: {
                "raw": None if overflow else 0.2,
                "overflow": overflow,
                "escalated": False,
                "scores": {"test": None if overflow else 0.2},
            }
            for qid in body["questions"]
        },
        "usage": {"input_tokens": 0 if overflow else 120, "output_tokens": len(body["questions"])},
        "escalation_skipped": fallback,
        "request_id": "request-test",
    }


@pytest.mark.parametrize("effort", ["low", "medium", "high"])
@pytest.mark.parametrize("use_async", [False, True])
@pytest.mark.parametrize("strict", [False, True])
@pytest.mark.parametrize("kind", ["noul", "boolean"])
async def test_explicit_questions_and_state(effort: str, use_async: bool, strict: bool, kind: str) -> None:
    questions = {"q7": {"type": kind, "instructions": {"task": "Useful?"}, "criteria": {"true": "Yes", "false": "No"}}}
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        assert request.url.path == "/v1/nimble/systemone"
        assert request.headers["api_key"] == "test"
        assert "authorization" not in request.headers
        assert request.headers["x-custom"] == "value"
        assert request.url.params["trace"] == "1"
        assert request.extensions["timeout"]["read"] == 7
        body = json.loads(request.content)
        assert body == {"state": STATE, "questions": questions, "model": f"nimble-codegrep-{effort}"}
        return httpx.Response(200, json=response_for(body))

    kwargs: Any = {
        "state": STATE,
        "questions": questions,
        "model": f"nimble-codegrep-{effort}",
        "extra_headers": {"x-custom": "value"},
        "extra_query": {"trace": "1"},
        "timeout": 7,
    }
    if use_async:
        async with nimble.AsyncNimble(
            api_key="test",
            _strict_response_validation=strict,
            http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
        ) as client:
            result = await client.with_options(max_retries=0).system_one(**kwargs)
    else:
        with nimble.Nimble(
            api_key="test",
            _strict_response_validation=strict,
            http_client=httpx.Client(transport=httpx.MockTransport(handler)),
        ) as client:
            result = client.with_options(max_retries=0).system_one(**kwargs)
    assert len(seen) == 1
    assert isinstance(result, CodegrepResponse)
    assert isinstance(result.details["q7"], CodegrepDetail)
    assert result.nouls["q7"].noul == 0.8
    assert result.details["q7"].raw == 0.2
    assert result.usage.output_tokens == 1
    assert result.request_id == "request-test"


@pytest.mark.parametrize("fallback,overflow", [(True, False), (False, True)])
def test_fallback_and_unscored_items_are_visible(fallback: bool, overflow: bool) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        assert body["model"] == "nimble-codegrep-medium"
        return httpx.Response(200, json=response_for(body, fallback=fallback, overflow=overflow))

    with nimble.Nimble(api_key="test", http_client=httpx.Client(transport=httpx.MockTransport(handler))) as client:
        result = client.system_one(
            model="nimble-codegrep-medium", state=STATE, questions={"q7": {"type": "noul", "instructions": "Useful?"}}
        )
    assert result.escalation_skipped is fallback
    assert result.details["q7"].overflow is overflow
    assert (result.details["q7"].raw is None) is overflow
    assert result.usage.input_tokens == (0 if overflow else 120)


@pytest.mark.parametrize("state", ["A file", {"query": "task"}])
def test_128_questions_supported(state: Any) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        assert len(body["questions"]) == 128
        return httpx.Response(200, json=response_for(body))

    with nimble.Nimble(api_key="test", http_client=httpx.Client(transport=httpx.MockTransport(handler))) as client:
        result = client.system_one(
            model="nimble-codegrep-medium",
            state=state,
            questions={f"q{i}": {"type": "boolean", "instructions": "Useful?"} for i in range(128)},
        )
    assert len(result.answers) == 128


@pytest.mark.parametrize(
    "overrides",
    [
        {"state": []},
        {"state": " "},
        {"state": "x" * 2_000_001},
        {"model": "nimble-codegrep-ultra"},
        {"questions": {}},
        {"questions": {str(i): {"type": "noul", "instructions": "Useful?"} for i in range(129)}},
        {"questions": {"q": {"type": "choice", "instructions": "Useful?"}}},
        {"questions": {"q": {"type": "noul", "instructions": " "}}},
        {"questions": {"q": {"type": "noul", "instructions": False}}},
        {"questions": {"q": {"type": "noul", "instructions": "Useful?", "criteria": {"true": 1}}}},
    ],
)
@pytest.mark.parametrize("use_async", [False, True])
async def test_invalid_input_not_sent(overrides: dict[str, Any], use_async: bool) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        pytest.fail(f"Unexpected request {request.url}")

    kwargs: Any = {
        "model": "nimble-codegrep-medium",
        "state": STATE,
        "questions": {"q7": {"type": "noul", "instructions": "Useful?"}},
        **overrides,
    }
    if use_async:
        async with nimble.AsyncNimble(
            api_key="test", http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler))
        ) as client:
            with pytest.raises(ValueError):
                await client.system_one(**kwargs)
    else:
        with nimble.Nimble(api_key="test", http_client=httpx.Client(transport=httpx.MockTransport(handler))) as client:
            with pytest.raises(ValueError):
                client.system_one(**kwargs)


@pytest.mark.parametrize(
    "field,value",
    [
        ("noul", True),
        ("noul", "0.8"),
        ("noul", 10**400),
        ("raw", "0.2"),
        ("raw", None),
        ("overflow", "false"),
        ("escalated", 1),
        ("scores", {"test": "0.2"}),
        ("input_tokens", True),
        ("output_tokens", -1),
        ("escalation_skipped", 1),
        ("answers", {}),
        ("details", {}),
    ],
)
def test_malformed_responses(field: str, value: Any) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        response = response_for(json.loads(request.content))
        if field == "noul":
            target = response["answers"]["q7"]
        elif field in {"raw", "overflow", "escalated", "scores"}:
            target = response["details"]["q7"]
        elif field in {"input_tokens", "output_tokens"}:
            target = response["usage"]
        else:
            target = response
        target[field] = value
        return httpx.Response(200, json=response)

    with nimble.Nimble(api_key="test", http_client=httpx.Client(transport=httpx.MockTransport(handler))) as client:
        with pytest.raises(ValueError, match="Invalid Codegrep response"):
            client.system_one(
                model="nimble-codegrep-medium",
                state=STATE,
                questions={"q7": {"type": "noul", "instructions": "Useful?"}},
            )


def test_standard_retry_behavior() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if len(seen) == 1:
            return httpx.Response(503, json={"detail": "starting"}, headers={"retry-after-ms": "1"})
        return httpx.Response(200, json=response_for(json.loads(request.content)))

    with nimble.Nimble(api_key="test", http_client=httpx.Client(transport=httpx.MockTransport(handler))) as client:
        result = client.system_one(
            model="nimble-codegrep-medium", state=STATE, questions={"q7": {"type": "noul", "instructions": "Useful?"}}
        )
    assert len(seen) == 2 and not result.escalation_skipped


@pytest.mark.parametrize("effort", ["low", "medium", "high"])
@pytest.mark.parametrize("use_async", [False, True])
@pytest.mark.parametrize("nested", [False, True])
@pytest.mark.parametrize("surface", ["normal", "raw", "streaming"])
@pytest.mark.parametrize("strict", [False, True])
async def test_system_one_model_selection(
    effort: str, use_async: bool, nested: bool, surface: str, strict: bool
) -> None:
    from bespokelabs.nimble.types.nimble import SystemOneResponse

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/nimble/systemone"
        assert request.headers["api_key"] == "test"
        body = json.loads(request.content)
        assert body["model"] == f"nimble-codegrep-{effort}"
        assert "effort" not in body
        return httpx.Response(200, json=response_for(body))

    kwargs: Any = {
        "state": STATE,
        "questions": {"q7": {"type": "boolean", "instructions": "Useful?"}},
        "model": f"nimble-codegrep-{effort}",
    }
    if use_async:
        async with nimble.AsyncNimble(
            api_key="test",
            _strict_response_validation=strict,
            http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
        ) as client:
            resource = client.nimble if nested else client
            if surface == "normal":
                result = await resource.system_one(**kwargs)
            elif surface == "raw":
                result = await (await resource.with_raw_response.system_one(**kwargs)).parse()
            else:
                async with resource.with_streaming_response.system_one(**kwargs) as response:
                    result = await response.parse()
    else:
        with nimble.Nimble(
            api_key="test",
            _strict_response_validation=strict,
            http_client=httpx.Client(transport=httpx.MockTransport(handler)),
        ) as client:
            resource = client.nimble if nested else client
            if surface == "normal":
                result = resource.system_one(**kwargs)
            elif surface == "raw":
                result = resource.with_raw_response.system_one(**kwargs).parse()
            else:
                with resource.with_streaming_response.system_one(**kwargs) as response:
                    result = response.parse()
    assert isinstance(result, SystemOneResponse)
    assert result.details["q7"].raw == 0.2
    assert result.nouls["q7"].noul == 0.8
    assert not result.escalation_skipped


def test_model_override_in_extra_body_keeps_typed_metadata() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        assert body["model"] == "nimble-codegrep-high"
        return httpx.Response(200, json=response_for(body, overflow=True))

    with nimble.Nimble(api_key="test", http_client=httpx.Client(transport=httpx.MockTransport(handler))) as client:
        result = client.system_one(
            state=STATE,
            questions={"q7": {"type": "noul", "instructions": "Useful?"}},
            extra_body={"model": "nimble-codegrep-high"},
        )
    assert result.details["q7"].overflow
    assert result.details["q7"].raw is None


def test_unknown_codegrep_model_is_rejected_locally() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        pytest.fail(f"Unexpected request: {request.url}")

    with nimble.Nimble(api_key="test", http_client=httpx.Client(transport=httpx.MockTransport(handler))) as client:
        with pytest.raises(ValueError, match="Unknown Codegrep model"):
            client.system_one(
                state=STATE,
                questions={"q7": {"type": "noul", "instructions": "Useful?"}},
                model="nimble-codegrep-ultra",
            )
