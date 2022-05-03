import logging
import os
import signal
from threading import Event

from prometheus_client import REGISTRY, start_http_server

from router_metrics.cpe_collector import CpeCollector
from router_metrics.pi_collector import RaspberryPiCollector

logging.basicConfig(level=logging.INFO)


def register_collectors():
    REGISTRY.register(
        CpeCollector("https://hirouter.net", "admin", os.environ["ROUTER_PASSWORD"])
    )
    REGISTRY.register(RaspberryPiCollector())


def run_forever():
    interrupted = Event()
    signal.signal(signal.SIGTERM, lambda *args: interrupted.set())
    interrupted.wait()


if __name__ == "__main__":
    register_collectors()
    start_http_server(8000)
    run_forever()
