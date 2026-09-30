# Minicheck

## Factcheck

Types:

```python
from bespokelabs.nimble.types.minicheck import FactcheckCreateResponse
```

Methods:

- <code title="post /v0/minicheck/factcheck">client.minicheck.factcheck.<a href="./src/bespokelabs/nimble/resources/minicheck/factcheck.py">create</a>(\*\*<a href="src/bespokelabs/nimble/types/minicheck/factcheck_create_params.py">params</a>) -> <a href="./src/bespokelabs/nimble/types/minicheck/factcheck_create_response.py">FactcheckCreateResponse</a></code>

# Nimble

Types:

```python
from bespokelabs.nimble.types.nimble import (
    NoulQuestion, ChoiceQuestion, ScoreQuestion,
    NoulAnswer, ChoiceAnswer, ScoreAnswer, SystemOneResponse,
)
```

Methods:

- `client.system_one(state=..., questions=..., model="nimble-latest") -> SystemOneResponse`
- `await async_client.system_one(state=..., questions=..., model="nimble-latest") -> SystemOneResponse`

Both call `POST /v1/nimble/systemone` and accept `extra_headers`, `extra_query`, `extra_body`,
and `timeout`. Raw-response and streaming-response variants follow the standard SDK interface.

## Direct clients

```python
from bespokelabs import nimble
from bespokelabs.nimble import Nimble, AsyncNimble
from bespokelabs.nimble.types import Effort, FactcheckResult, FactcheckResponse
```

- `nimble.Nimble()` and `nimble.AsyncNimble()` expose `system_one` directly.
- `client.factcheck(context=..., claims=[...], effort="medium") -> FactcheckResponse`
- `await async_client.factcheck(context=..., claims=[...], effort="medium") -> FactcheckResponse`

Fact checking sends 1–64 claims with shared context in one request. `results` contains `claim` and `support_prob` for
each input, in input order. The response includes model, usage, and request ID.
All three efforts (`low`, `medium`, `high`) call `/v1/nimble/factcheck`.
`split_claims=True` checks sentences separately and returns the lowest score for
each original claim. This method accepts `extra_headers`, `extra_query`, and
`timeout`; the effort selects the model. Results include the selected effort,
billable input usage, support decisions, and available escalation metadata.

`BespokeLabs` / `AsyncBespokeLabs` and `Client` / `AsyncClient` are compatibility
aliases. The nested `client.nimble.system_one` interface remains available.

## Codegrep

```python
from bespokelabs.nimble.types import CodegrepState, CodegrepQuestion, CodegrepDetail, CodegrepResponse
```

- `client.codegrep(state=..., questions={...}, effort="medium") -> CodegrepResponse`
- `await async_client.codegrep(state=..., questions={...}, effort="medium") -> CodegrepResponse`

Sends explicit state and named questions to `POST /v1/nimble/codegrep`. Supports
`low`, `medium`, and `high` effort, 1–128 `noul`/`boolean` questions, and a string or
object state. The response preserves question IDs in `answers` and `details`,
with usage and a visible `escalation_skipped` flag for medium fallback. Overflow
answers are 1.0 with `raw=None` and `overflow=True`.

Both helpers accept `extra_headers`, `extra_query`, and `timeout`.
