import logging
import sys
import time

logging.OK = logging.INFO + 1
logging.STATUS = logging.INFO + 2

logging.addLevelName(logging.OK, "OK")
logging.addLevelName(logging.STATUS, "STATUS")


def ok(self, message, *args, **kws):
    self._log(logging.OK, message, args, **kws)


def status(self, message, *args, **kws):
    self._log(logging.STATUS, message, args, **kws)


logging.Logger.ok = ok
logging.Logger.status = status


class Colorscheme:
    GRAY = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[0;33m"
    BLUE = "\033[0;34m"
    MAGENTA = "\033[0;35m"
    AQUA = "\033[0;36m"
    WHITE = "\033[0;37m"


def setup_global_logging(verbose: bool, quiet: bool, color: bool) -> logging.Logger:
    "setup logging and deal with logging behaviours in MacOS python 3.8 and below"

    # setup logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # log line templates
    log_line_info = "%(color_on)s%(message)s%(color_off)s"
    log_line_debug = (
        "%(color_on)s%(asctime)s %(levelname)-8s %(message)s (%(filename)s:%(lineno)d)%(color_off)s"
    )

    # get level
    level = logging.INFO
    if verbose:
        level = logging.DEBUG
        console_log_template = log_line_debug
    elif quiet:
        level = logging.ERROR
        console_log_template = log_line_info
    else:
        console_log_template = log_line_info

    # setup console handler
    console_log_output = sys.stdout
    console_handler = logging.StreamHandler(console_log_output)
    console_handler.setLevel(level)

    console_formatter = LogFormatter(fmt=console_log_template, color=color)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # setup log file handler
    # if log_file:
    #     # check if log path is valid
    #     parts = log_file.split(os.sep)
    #     if len(parts) > 1:
    #         path = os.sep.join(parts[0:-1])
    #         os.makedirs(path, exist_ok=True)

    #     logfile_handler = logging.FileHandler(log_file + ".log", mode="w")
    #     logfile_handler.setLevel(logging.DEBUG)

    #     logfile_formatter = LogFormatter(fmt=log_line_debug, color=False)
    #     logfile_handler.setFormatter(logfile_formatter)
    #     logger.addHandler(logfile_handler)

    if verbose and quiet:
        logger.warning("Got '--verbose' and '--quiet' as arguments. Using mode: verbose")
    logger.debug(f"Using logging level: {logging.getLevelName(level)}")

    return logger


class LogFormatter(logging.Formatter):
    """
    supports colored formatting
    """

    COLOR_CODES = {
        logging.DEBUG: Colorscheme.GRAY,
        logging.INFO: Colorscheme.WHITE,
        logging.OK: Colorscheme.GREEN,
        logging.STATUS: Colorscheme.BLUE,
        logging.WARNING: Colorscheme.YELLOW,
        logging.ERROR: Colorscheme.RED,
        logging.CRITICAL: Colorscheme.MAGENTA,
    }

    RESET_CODE = "\033[0m"

    def __init__(self, color, *args, **kwargs):
        super(LogFormatter, self).__init__(*args, **kwargs)
        self.color = color

    def format(self, record, *args, **kwargs):
        if self.color == True and record.levelno in self.COLOR_CODES:
            record.color_on = self.COLOR_CODES[record.levelno]
            record.color_off = self.RESET_CODE
        else:
            record.color_on = ""
            record.color_off = ""
        return super(LogFormatter, self).format(record, *args, **kwargs)


def setup_process_logging(index: int, color: bool):
    # setup logger
    logger = logging.getLogger(f"process-{index}")
    logger.setLevel(logging.INFO)

    # log line templates
    console_log_template = "%(color_on)s%(message)s%(color_off)s"

    # setup console handler
    console_handler = ConsoleLoggingHandler(index)

    console_formatter = LogFormatter(fmt=console_log_template, color=color)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger


class ConsoleLoggingHandler(logging.Handler):
    def __init__(self, line_number):
        super().__init__()
        self.line_number = line_number

    def emit(self, record):
        try:
            msg = self.format(record)
            print_in_line(self.line_number, f"\033[30C{msg}", overwrite_line=True)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)


def print_in_line(line: int, msg: str, overwrite_line: bool = True):
    assert line > 0
    move_down = f"\033[{line-1}B" if not line == 1 else ""
    move_up = f"\033[{line}A"
    carry = "\033[K" if overwrite_line else ""
    print(f"{move_down}{msg}{carry}{move_up}")


def monitoring(num_processes, shared_data):
    start_time = time.time()
    while any(shared_data):
        elapsed_time = time.time() - start_time
        for i in range(num_processes):
            if shared_data[i]:
                msg = f" · ({elapsed_time:05.2f} s)"
                print_in_line(i + 1, msg, overwrite_line=False)
