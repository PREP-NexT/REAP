import logging
import time
from pathlib import Path


def setup_logging():
    """Configure root logger to write to ``log/main_<timestamp>.log`` and stderr.

    Idempotent: repeat calls within the same process are no-ops. Without this
    guard, callers in a loop would attach a new ``StreamHandler`` each time
    and every log line would be printed once per accumulated handler.
    """
    root = logging.getLogger()
    if root.handlers:
        return

    log_dir = Path('log')
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f'main_{time.strftime("%Y-%m-%d-%H-%M-%S")}.log'

    fmt = '%(asctime)s %(levelname)s: %(message)s'
    datefmt = '%Y-%m-%d %H:%M:%S'
    logging.basicConfig(filename=log_file, level=logging.INFO,
                        format=fmt, datefmt=datefmt)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(fmt, datefmt))
    root.addHandler(console)


def log_and_time(func):
    """Decorator that logs runtime of ``func`` in minutes."""
    def wrapper(*args, **kwargs):
        logging.info("Start solving model ...")
        start_time = time.time()
        result = func(*args, **kwargs)
        logging.info(
            "Completed! Total runtime: %s minutes",
            round((time.time() - start_time) / 60, 2),
        )
        return result
    return wrapper


def log_parameter_info(config_data):
    """Log the high-level config values used for this run."""
    logging.info("Set parameter solver to value %s",
                 config_data['solver_parameters']['solver'])
    logging.info("Set parameter input folder to value %s",
                 config_data['general_parameters']['input_folder'])
    logging.info("Set parameter output_filename to value %s.nc",
                 config_data['general_parameters']['output_filename'])
    logging.info("Set parameter time_length to value %s",
                 config_data['general_parameters']['hour'])
