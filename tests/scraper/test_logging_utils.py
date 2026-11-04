import logging

from scraper.logging_utils import _log_level


def test_log_level_defaults_to_info(monkeypatch):
    monkeypatch.delenv("LOG_LEVEL", raising=False)

    assert _log_level() == logging.INFO


def test_log_level_reads_environment(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "debug")

    assert _log_level() == logging.DEBUG


def test_log_level_falls_back_for_invalid_values(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "definitely-not-a-level")

    assert _log_level() == logging.INFO
