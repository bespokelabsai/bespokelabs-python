"""Keep the SDK from taking ownership of the shared Bespoke Labs namespace."""

import sys
import subprocess
from pathlib import Path

import pytest


@pytest.mark.parametrize("sdk_first", [True, False])
def test_separate_namespace_portions(tmp_path: Path, sdk_first: bool) -> None:
    source = Path(__file__).resolve().parents[1] / "src"
    siblings = tmp_path / "siblings"
    for name in ("curator", "sandbox"):
        package = siblings / "bespokelabs" / name
        package.mkdir(parents=True)
        (package / "__init__.py").write_text(f"NAME = {name!r}\n")

    paths = [str(source), str(siblings)]
    if not sdk_first:
        paths.reverse()

    # A fresh interpreter makes import order and root ownership observable.
    code = f"""
import sys
sys.path[:0] = {paths!r}
import bespokelabs
from bespokelabs import curator, sandbox, nimble
from bespokelabs.nimble import BespokeLabs, AsyncBespokeLabs, APIError
from bespokelabs.nimble.types.nimble import Question

assert bespokelabs.__file__ is None
assert curator.NAME == 'curator'
assert sandbox.NAME == 'sandbox'
assert APIError.__module__ == 'bespokelabs.nimble'
assert nimble.Nimble is BespokeLabs
assert nimble.AsyncNimble is AsyncBespokeLabs
with nimble.Nimble(api_key='test') as client:
    assert callable(client.system_one)
    assert callable(client.factcheck)
assert callable(AsyncBespokeLabs)
"""
    subprocess.run([sys.executable, "-I", "-c", code], check=True, capture_output=True, text=True)
