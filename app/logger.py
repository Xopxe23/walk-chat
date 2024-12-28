import logging


def get_logger() -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s:     %(message)s %(asctime)s",
        handlers=[
            logging.StreamHandler(),
        ],
    )

    logging.getLogger('aiokafka').setLevel(logging.WARNING)
    logging.getLogger('brokers').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)

    logger = logging.getLogger("walk-profile")
    return logger
