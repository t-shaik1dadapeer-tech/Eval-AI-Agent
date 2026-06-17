"""Intentional failing test for D3 failure-mode demonstration only."""


def test_intentional_failure() -> None:
    assert 1 == 2, "deliberate failure for CI pipeline demo"
