import pytest
from prometheus_client.core import GaugeMetricFamily

from router_metrics import cpe_collector


def gauge(name, documentation, labels, label_values: dict):
    g = GaugeMetricFamily(name, documentation, labels=labels)
    for k, v in label_values.items():
        g.add_metric([k], v)
    return g


@pytest.mark.parametrize(
    "response, expected",
    (
        ({}, []),
        (
            {"nrdlbandwidth": "100MHz"},
            [
                GaugeMetricFamily(
                    "signal_nrdlbandwidth",
                    "Signal metrics: nrdlbandwidth",
                    unit="MHz",
                    value=100,
                )
            ],
        ),
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
                    value=4,
                )
            ],
        ),
        (
            {"nei_cellid": "No1:236No2:234No3:20No4:426"},
            [
                gauge(
                    "signal_nei_cellid",
                    "Signal metrics: nei_cellid",
                    labels=["No"],
                    label_values={"1": 236, "2": 234, "3": 20, "4": 426},
                )
            ],
        ),
    ),
    ids=lambda x: str(x) if isinstance(x, dict) else None,
)
def test_parse_signal_metrics(response, expected):
    assert list(cpe_collector.parse_signal_metrics(response)) == expected
