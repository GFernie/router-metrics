import logging
import subprocess
from enum import Flag

from prometheus_client.metrics_core import GaugeMetricFamily

log = logging.getLogger(__name__)


class RaspberryPiCollector:
    def collect(self):
        try:
            get_throttled = subprocess.run(
                # TODO Inject private key and host key.
                "ssh host.docker.internal vcgencmd get_throttled",
                shell=True,
                capture_output=True,
                check=True,
            ).stdout
        except subprocess.CalledProcessError as e:
            e.__traceback__ = None
            log.warning("Failed to connect to host", exc_info=e)
            return
        yield from parse_get_throttled(get_throttled)


def parse_get_throttled(response):
    try:
        throttled = Throttled(int(response, base=16))
    except (TypeError, ValueError):
        log.warning("Could not parse get_throttled %r", response)
        return
    for flag, set in throttled.flags:
        yield GaugeMetricFamily(
            f"raspberry_pi_vcgencmd_get_throttled_{flag.name.lower()}",
            f"Raspberry Pi command `vcgencmd get_throttled`, flag {flag.name}, bitmask"
            f" {flag.value:#x}.",
            set,
        )


class Throttled(Flag):
    UNDER_VOLTAGE_DETECTED = 0x1
    ARM_FREQUENCY_CAPPED = 0x2
    CURRENTLY_THROTTLED = 0x4
    SOFT_TEMPERATURE_LIMIT_ACTIVE = 0x8
    UNDER_VOLTAGE_HAS_OCCURRED = 0x10000
    ARM_FREQUENCY_CAPPING_HAS_OCCURRED = 0x20000
    THROTTLING_HAS_OCCURRED = 0x40000
    SOFT_TEMPERATURE_LIMIT_HAS_OCCURRED = 0x80000

    @property
    def flags(self):
        """Iterate tuple of (flag, is set) for all flags."""
        yield from ((f, f in self) for f in self.__class__)
