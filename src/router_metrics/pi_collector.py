import logging
import re
import subprocess
from enum import Flag

from prometheus_client.metrics_core import GaugeMetricFamily

log = logging.getLogger(__name__)


class RaspberryPiCollector:
    def collect(self):
        try:
            get_throttled = run_host_process("vcgencmd get_throttled")
            measure_temp = run_host_process("vcgencmd measure_temp")
            measure_volts = run_host_process("vcgencmd measure_volts")
        except subprocess.CalledProcessError as e:
            e.__traceback__ = None
            log.warning("Failed to scrape host", exc_info=e)
            return
        yield from parse_get_throttled(get_throttled)
        yield parse_measure_temp(measure_temp)
        yield parse_measure_volts(measure_volts)

    def describe(self):
        """Stop collect being called for describe on init."""
        return []


def run_host_process(command):
    return subprocess.run(
        f"nsenter -t 1 -m {command}",
        shell=True,
        capture_output=True,
        check=True,
    ).stdout.decode()


def parse_get_throttled(response):
    if match := re.match(r"throttled=(0x.+)", response):
        hex_flags = match.group(1)
    else:
        log.warning("Could not parse vcgencmd get_throttled %r", response)
        return
    try:
        throttled = Throttled(int(hex_flags, base=16))
    except (TypeError, ValueError):
        log.warning("Could not parse vcgencmd get_throttled %r", response)
        return
    for flag, set in throttled.flags:
        yield GaugeMetricFamily(
            f"raspberry_pi_vcgencmd_get_throttled_{flag.name.lower()}",
            documentation=(
                f"Raspberry Pi command `vcgencmd get_throttled`, flag {flag.name},"
                f" bitmask {flag.value:#x}."
            ),
            value=set,
        )


def parse_measure_temp(response):
    if match := re.match(r"temp=([0-9\.]+)'C", response):
        value = match.group(1)
    else:
        log.warning("Could not parse vcgencmd measure_temp %r", response)
        return
    return GaugeMetricFamily(
        "raspberry_py_vcgencmd_measure_temp",
        documentation="Raspberry Pi command `vcgencmd measure_temp`",
        value=float(value),
        unit="C",
    )


def parse_measure_volts(response):
    if match := re.match(r"volt=([0-9\.]+)V", response):
        value = match.group(1)
    else:
        log.warning("Could not parse vcgencmd measure_volts %r", response)
        return
    return GaugeMetricFamily(
        "raspberry_py_vcgencmd_measure_volts",
        documentation="Raspberry Pi command `vcgencmd measure_volts`",
        value=float(value),
        unit="V",
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
