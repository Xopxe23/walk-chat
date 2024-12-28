from abc import ABC, abstractmethod


class KafkaProducerInterface(ABC):
    likes_topic: str
    matches_topic: str

    @abstractmethod
    async def sent_message(self, topic: str, data: dict) -> None:
        raise NotImplementedError
