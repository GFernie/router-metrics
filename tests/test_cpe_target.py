import pytest
from prometheus_client.core import GaugeMetricFamily

import cpe_target


@pytest.mark.parametrize(
    "response, expected",
    (
        ({}, []),
        (
            {"scc_pci": "0x1C3"},
            [
                GaugeMetricFamily(
                    "signal_scc_pci", "Signal metrics: scc_pci", unit="hex", value=451
                )
            ],
        ),
        (
            {"transmode": "TM[4]"},
            [
                GaugeMetricFamily(
                    "signal_transmode",
                    "Signal metrics: transmode",
                    unit="TM",
                    value="4",
                )
            ],
        ),
    ),
)
def test_parse_signal_metrics(response, expected):
    assert list(cpe_target.parse_signal_metrics(response)) == expected
