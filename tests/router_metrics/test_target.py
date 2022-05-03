from unittest import mock

from router_metrics import target
from router_metrics.cpe_collector import CpeCollector
from router_metrics.pi_collector import RaspberryPiCollector


@mock.patch.dict("os.environ", {"ROUTER_PASSWORD": "foo"})
@mock.patch("router_metrics.target.CpeCollector", autospec=True)
@mock.patch("router_metrics.target.REGISTRY")
def test_register_collectors(mock_registry, cpe_collector):
    target.register_collectors()
    assert cpe_collector.mock_calls == [
        mock.call("https://hirouter.net", "admin", "foo")
    ]
    assert isinstance(mock_registry.register.mock_calls[0].args[0], CpeCollector)
    assert isinstance(
        mock_registry.register.mock_calls[1].args[0], RaspberryPiCollector
    )
