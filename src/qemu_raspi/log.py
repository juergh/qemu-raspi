# log

import logging
import sys

import colorlog

LOG = colorlog.getLogger("qemu-raspi")
if not LOG.handlers:
    LOG.addHandler(logging.NullHandler())


def enable_logging(verbose=False, debug=False):
    if not verbose and not debug:
        return

    formatter = colorlog.ColoredFormatter(
        fmt="%(log_color)s%(message)s",
        log_colors={
            "DEBUG": "light_purple",
            "INFO": "light_cyan",
            "WARNING": "light_yellow",
            "ERROR": "light_red",
        },
    )
    console_handler = colorlog.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    LOG.addHandler(console_handler)
    LOG.setLevel(logging.DEBUG if debug else logging.INFO)


debug = LOG.debug
info = LOG.info
warn = LOG.warning
error = LOG.error
