# Minicheck

## Factcheck

Types:

```python
from bespokelabs.types.minicheck import FactcheckCreateResponse
```

Methods:

- <code title="post /v0/minicheck/factcheck">client.minicheck.factcheck.<a href="./src/bespokelabs/resources/minicheck/factcheck.py">create</a>(\*\*<a href="src/bespokelabs/types/minicheck/factcheck_create_params.py">params</a>) -> <a href="./src/bespokelabs/types/minicheck/factcheck_create_response.py">FactcheckCreateResponse</a></code>

# Nimble

Types:

```python
from bespokelabs.types.nimble import (
    NoulQuestion, ChoiceQuestion, ScoreQuestion,
    NoulAnswer, ChoiceAnswer, ScoreAnswer, SystemOneResponse,
)
```

Methods:

- `client.nimble.system_one(state=..., questions=..., model="nimble-latest") -> SystemOneResponse`
- `await async_client.nimble.system_one(state=..., questions=..., model="nimble-latest") -> SystemOneResponse`

Both call `POST /v1/nimble/systemone` and accept `extra_headers`, `extra_query`, `extra_body`,
and `timeout`. Raw-response and streaming-response variants follow the standard SDK interface.
