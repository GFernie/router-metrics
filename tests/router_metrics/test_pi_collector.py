import io
import logging

import pytest
from prometheus_client.metrics_core import GaugeMetricFamily

from router_metrics import pi_collector


@pytest.fixture()
def log_stream():
    logger = logging.root
    logger_level = logger.level
    logger.setLevel(logging.NOTSET)
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
    logger.addHandler(handler)
    yield stream
    logger.setLevel(logger_level)
    logger.removeHandler(handler)


def test_parse_get_throttled():
    assert list(pi_collector.parse_get_throttled("throttled=0x50003\n")) == [
        GaugeMetricFamily(
            "raspberry_pi_vcgencmd_get_throttled_under_voltage_detected",
            documentation=(
                "Raspberry Pi command `vcgencmd get_throttled`, flag"
                " UNDER_VOLTAGE_DETECTED, bitmask 0x1."
            ),
            value=True,
        ),
        GaugeMetricFamily(
            "raspberry_pi_vcgencmd_get_throttled_arm_frequency_capped",
            documentation=(
                "Raspberry Pi command `vcgencmd get_throttled`, flag"
                " ARM_FREQUENCY_CAPPED, bitmask 0x2."
            ),
            value=True,
        ),
        GaugeMetricFamily(
            "raspberry_pi_vcgencmd_get_throttled_currently_throttled",
            documentation=(
                "Raspberry Pi command `vcgencmd get_throttled`, flag"
                " CURRENTLY_THROTTLED, bitmask 0x4."
            ),
            value=False,
        ),
        GaugeMetricFamily(
            "raspberry_pi_vcgencmd_get_throttled_soft_temperature_limit_active",
            documentation=(
                "Raspberry Pi command `vcgencmd get_throttled`, flag"
                " SOFT_TEMPERATURE_LIMIT_ACTIVE, bitmask 0x8."
            ),
            value=False,
        ),
        GaugeMetricFamily(
            "raspberry_pi_vcgencmd_get_throttled_under_voltage_has_occurred",
            documentation=(
                "Raspberry Pi command `vcgencmd get_throttled`, flag"
                " UNDER_VOLTAGE_HAS_OCCURRED, bitmask 0x10000."
            ),
            value=True,
        ),
        GaugeMetricFamily(
            "raspberry_pi_vcgencmd_get_throttled_arm_frequency_capping_has_occurred",
            documentation=(
                "Raspberry Pi command `vcgencmd get_throttled`, flag"
                " ARM_FREQUENCY_CAPPING_HAS_OCCURRED, bitmask 0x20000."
            ),
            value=False,
        ),
        GaugeMetricFamily(
            "raspberry_pi_vcgencmd_get_throttled_throttling_has_occurred",
            documentation=(
                "Raspberry Pi command `vcgencmd get_throttled`, flag"
                " THROTTLING_HAS_OCCURRED, bitmask 0x40000."
            ),
            value=True,
        ),
        GaugeMetricFamily(
            "raspberry_pi_vcgencmd_get_throttled_soft_temperature_limit_has_occurred",
            documentation=(
                "Raspberry Pi command `vcgencmd get_throttled`, flag"
                " SOFT_TEMPERATURE_LIMIT_HAS_OCCURRED, bitmask 0x80000."
            ),
            value=False,
        ),
    ]


def test_parse_get_throttled_ok():
    assert not any(
        s.value
        for m in pi_collector.parse_get_throttled("throttled=0x0\n")
        for s in m.samples
    )


def test_parse_get_throttled_error(log_stream):
    list(pi_collector.parse_get_throttled("foo"))
    assert (
        log_stream.getvalue()
        == "WARNING:router_metrics.pi_collector:Could not parse vcgencmd get_throttled"
        " 'foo'\n"
    )


def test_parse_measure_temp():
    assert pi_collector.parse_measure_temp("temp=50.5'C\n") == GaugeMetricFamily(
        "raspberry_pi_vcgencmd_measure_temp",
        documentation="Raspberry Pi command `vcgencmd measure_temp`",
        value=50.5,
        unit="C",
    )


def test_parse_measure_volts():
    assert pi_collector.parse_measure_volts("volt=1.3312V\n") == GaugeMetricFamily(
        "raspberry_pi_vcgencmd_measure_volts",
        documentation="Raspberry Pi command `vcgencmd measure_volts`",
        value=1.3312,
        unit="V",
    )


def test_throttled():
    assert list(pi_collector.Throttled(0x50003).flags) == [
        (pi_collector.Throttled.UNDER_VOLTAGE_DETECTED, True),
        (pi_collector.Throttled.ARM_FREQUENCY_CAPPED, True),
        (pi_collector.Throttled.CURRENTLY_THROTTLED, False),
        (pi_collector.Throttled.SOFT_TEMPERATURE_LIMIT_ACTIVE, False),
        (pi_collector.Throttled.UNDER_VOLTAGE_HAS_OCCURRED, True),
        (pi_collector.Throttled.ARM_FREQUENCY_CAPPING_HAS_OCCURRED, False),
        (pi_collector.Throttled.THROTTLING_HAS_OCCURRED, True),
        (pi_collector.Throttled.SOFT_TEMPERATURE_LIMIT_HAS_OCCURRED, False),
    ]
