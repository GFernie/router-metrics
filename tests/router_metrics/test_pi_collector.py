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
    assert list(pi_collector.parse_get_throttled("0x50003")) == [
        GaugeMetricFamily(
            "raspberry_pi_vcgencmd_get_throttled_under_voltage_detected",
            "Raspberry Pi command `vcgencmd get_throttled`, flag"
            " UNDER_VOLTAGE_DETECTED, bitmask 0x1.",
            True,
        ),
        GaugeMetricFamily(
            "raspberry_pi_vcgencmd_get_throttled_arm_frequency_capped",
            "Raspberry Pi command `vcgencmd get_throttled`, flag ARM_FREQUENCY_CAPPED,"
            " bitmask 0x2.",
            True,
        ),
        GaugeMetricFamily(
            "raspberry_pi_vcgencmd_get_throttled_currently_throttled",
            "Raspberry Pi command `vcgencmd get_throttled`, flag CURRENTLY_THROTTLED,"
            " bitmask 0x4.",
            False,
        ),
        GaugeMetricFamily(
            "raspberry_pi_vcgencmd_get_throttled_soft_temperature_limit_active",
            "Raspberry Pi command `vcgencmd get_throttled`, flag"
            " SOFT_TEMPERATURE_LIMIT_ACTIVE, bitmask 0x8.",
            False,
        ),
        GaugeMetricFamily(
            "raspberry_pi_vcgencmd_get_throttled_under_voltage_has_occurred",
            "Raspberry Pi command `vcgencmd get_throttled`, flag"
            " UNDER_VOLTAGE_HAS_OCCURRED, bitmask 0x10000.",
            True,
        ),
        GaugeMetricFamily(
            "raspberry_pi_vcgencmd_get_throttled_arm_frequency_capping_has_occurred",
            "Raspberry Pi command `vcgencmd get_throttled`, flag"
            " ARM_FREQUENCY_CAPPING_HAS_OCCURRED, bitmask 0x20000.",
            False,
        ),
        GaugeMetricFamily(
            "raspberry_pi_vcgencmd_get_throttled_throttling_has_occurred",
            "Raspberry Pi command `vcgencmd get_throttled`, flag"
            " THROTTLING_HAS_OCCURRED, bitmask 0x40000.",
            True,
        ),
        GaugeMetricFamily(
            "raspberry_pi_vcgencmd_get_throttled_soft_temperature_limit_has_occurred",
            "Raspberry Pi command `vcgencmd get_throttled`, flag"
            " SOFT_TEMPERATURE_LIMIT_HAS_OCCURRED, bitmask 0x80000.",
            False,
        ),
    ]


def test_parse_get_throttled_ok():
    assert not any(
        s.value for m in pi_collector.parse_get_throttled("0x0") for s in m.samples
    )


def test_parse_get_throttled_error(log_stream):
    list(pi_collector.parse_get_throttled("foo"))
    assert (
        log_stream.getvalue()
        == "WARNING:router_metrics.pi_collector:Could not parse get_throttled 'foo'\n"
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
