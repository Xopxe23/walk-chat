from unittest.mock import MagicMock


def get_mocked_logger():
    logger = MagicMock()
    logger.info = MagicMock()
    logger.debug = MagicMock()
    logger.error = MagicMock()
    logger.warning = MagicMock()
    return logger
