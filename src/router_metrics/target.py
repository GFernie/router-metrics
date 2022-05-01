import logging
import os
import re
import signal
from datetime import timedelta
from threading import Event

import requests
from huawei_lte_api.Client import Client
from huawei_lte_api.Connection import Connection
from prometheus_client import start_http_server
from prometheus_client.core import (
    REGISTRY,
    CounterMetricFamily,
    GaugeMetricFamily,
    InfoMetricFamily,
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class CpeCollector:
    def __init__(self, url, username=None, password=None):
        self.connection = lambda: Connection(url, username=username, password=password)

    def collect(self):
        try:
            with self.connection() as connection:
                client = Client(connection)
                device_info = client.device.information()
                device_signal = client.device.signal()
                monitoring_traffic = client.monitoring.traffic_statistics()
                device_boot_time = client.device.boot_time()
        except requests.exceptions.ConnectionError as e:
            e.__traceback__ = None
            e.__cause__ = None
            log.warning("Failed to connect to router", exc_info=e)
            return
        log.debug("Device Information: %s", device_info)
        log.debug("Device Signal: %s", device_signal)
        device_info = {k: v for k, v in device_info.items() if v is not None}
        yield InfoMetricFamily(
            "device_info", "Export of device info endpoint", value=device_info
        )
        yield from parse_signal_metrics(device_signal)
        yield from parse_monitoring_traffic(monitoring_traffic)
        yield from parse_device_boot_time(device_boot_time)

    def describe(self):
        """Stop collect being called for describe on init."""
        return []


def parse_signal_metrics(response):
    for name, v in response.items():
        if v is None:
            log.debug("Skipping null metric %s", name)
            continue
        for v in v.split():
            k = name
            if label_values := dict(re.findall("No([0-9]+):([0-9]+)", v)):
                g = GaugeMetricFamily(
                    f"signal_{k}", f"Signal metrics: {name}", labels=["No"]
                )
                for label, v in label_values.items():
                    g.add_metric([label], float(v))
                yield g
                continue
            if match := re.match(r"^(.+):(.+)$", v):
                _k, v = match.groups()
                k = f"{k}_{_k}"
            unit = ""
            if match := re.match(r"^([A-Z]+)\[(.+)]$", v):
                unit, v = match.groups()
            if match := re.match(r"^(-?[0-9]+\.?[0-9]*)([a-zA-Z]+)$", v):
                v, unit_suffix = match.groups()
                unit = append_unit(unit, unit_suffix)
            if re.match(r"^0x[A-F0-9]+$", v):
                v = int(v, base=16)
                unit = append_unit(unit, "hex")
            try:
                v = float(v)
            except ValueError:
                log.warning("Failed to parse %s: %s", k, v)
                continue
            yield GaugeMetricFamily(
                f"signal_{k}", f"Signal metrics: {name}", unit=unit, value=v
            )


def append_unit(unit, suffix):
    if unit:
        return f"{unit}_{suffix}"
    return suffix


def parse_monitoring_traffic(response):
    name_prefix = "monitoring_traffic_statistics_"
    help_prefix = "Endpoint monitoring/traffic-statistics, field "
    metrics = (
        ("CurrentConnectTime", "current_connect_time", "second"),
        ("TotalDownload", "download", "byte"),
        ("TotalUpload", "upload", "byte"),
        ("TotalConnectTime", "connect_time", "second"),
    )
    for field, name, unit in metrics:
        yield CounterMetricFamily(
            name_prefix + name, help_prefix + field, unit=unit, value=response[field]
        )


def parse_device_boot_time(response):
    h, m, s = re.match(
        r"^\[(\d+)\]:\[(\d+)\]:\[(\d+)\]$", response["boot_time"]
    ).groups()
    uptime = timedelta(hours=int(h), minutes=int(m), seconds=int(s)).total_seconds()
    yield CounterMetricFamily(
        "device_boot_time",
        "Endpoint device/boot_time, field boot_time",
        unit="second",
        value=uptime,
    )


if __name__ == "__main__":
    REGISTRY.register(
        CpeCollector("https://hirouter.net", "admin", os.environ["ROUTER_PASSWORD"])
    )
    start_http_server(8000)
    interrupted = Event()
    signal.signal(signal.SIGTERM, lambda *args: interrupted.set())
    interrupted.wait()
