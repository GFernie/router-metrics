from unittest import mock

from router_metrics import target
from router_metrics.cpe_collector import CpeCollector


@mock.patch.dict("os.environ", {"ROUTER_PASSWORD": "foo"})
@mock.patch("router_metrics.target.REGISTRY")
def test_register_collectors(mock_registry):
    target.register_collectors()
    assert mock_registry.register.mock_calls == [
        mock.call(CpeCollector("https://hirouter.net", "admin", "foo"))
    ]
