import pytest

import cpe_target


@pytest.mark.parametrize(
    "response, expected",
    (
        ({}, []),
    )
)
def test_parse_signal_metrics(response, expected):
    assert list(cpe_target.parse_signal_metrics(response)) == expected
