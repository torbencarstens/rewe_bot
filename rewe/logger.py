import logging
import sys


class Logger(logging.Logger):
    def __init__(self, name, level="INFO"):
        super().__init__(name)

        ch = logging.StreamHandler(sys.stdout)

        formatting = "[rewe_bot] %(levelname)s\t%(module)s.%(funcName)s\tLine=%(lineno)d | %(message)s"
        formatter = logging.Formatter(formatting)
        ch.setFormatter(formatter)

        self.addHandler(ch)
        self.setLevel(level)
