import logging
import sys

def setup_logger():
    logger = logging.getLogger('autobaza')
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Вивід у консоль (для Docker logs на AWS)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

log = setup_logger()