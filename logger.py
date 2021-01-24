import logging

logger = logging.getLogger(__name__)

# the handler determines where the logs go: stdout/file
file_handler = logging.FileHandler("debug.log")

logger.setLevel(logging.DEBUG)
file_handler.setLevel(logging.DEBUG)

# the formatter determines what our logs will look like
fmt_file = (
    "%(levelname)s %(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(message)s"
)

file_formatter = logging.Formatter(fmt_file)

# here we hook everything together
file_handler.setFormatter(file_formatter)

logger.addHandler(file_handler)