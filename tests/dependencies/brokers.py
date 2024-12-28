from unittest.mock import MagicMock


def get_mocked_kafka_consumer():
    mock_producer = MagicMock()
    mock_producer.start = MagicMock()
    mock_producer.stop = MagicMock()
    mock_producer.subscribe = MagicMock()
    mock_producer.consume_messages = MagicMock()
    mock_producer.process_messages = MagicMock()
    return mock_producer


def get_mocked_kafka_producer():
    mock_producer = MagicMock()
    mock_producer.start = MagicMock()
    mock_producer.stop = MagicMock()
    mock_producer.send = MagicMock()
    mock_producer.send_message = MagicMock()
    return mock_producer
