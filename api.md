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

Fact checking sends 1–64 claims in one `POST /v1/nimble/systemone` request as Noul
questions with shared context. `results` contains `claim` and `support_prob` for
each input, in input order. The response includes model, usage, and request ID.
Only `medium` is implemented; `low` and `high` raise `NotImplementedError` pending
a defined effort strategy. This helper also accepts `model`, `extra_headers`,
`extra_query`, and `timeout`. It has no raw/streaming variant.

`BespokeLabs` / `AsyncBespokeLabs` and `Client` / `AsyncClient` are compatibility
aliases. The nested `client.nimble.system_one` interface remains available.
