"""Minimal structured logger for test steps — also surfaces steps in the Allure report."""

import logging

import allure

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")


class Logger:
    def __init__(self, name: str = "python-appium"):
        self._logger = logging.getLogger(name)

    def step(self, message: str):
        self._logger.info(f"STEP: {message}")
        with allure.step(message):
            pass

    def substep(self, message: str):
        self._logger.info(f"  - {message}")
        with allure.step(message):
            pass

    def info(self, message: str):
        self._logger.info(message)

    def success(self, message: str):
        self._logger.info(f"PASS: {message}")

    def warn(self, message: str):
        self._logger.warning(message)

    def error(self, message: str):
        self._logger.error(message)

    def data(self, key: str, value):
        self._logger.info(f"{key} = {value}")
        allure.attach(str(value), name=key, attachment_type=allure.attachment_type.TEXT)
