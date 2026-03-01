from abc import ABC, abstractmethod
from typing import List
from models import Gift

class BaseParser(ABC):
    @abstractmethod
    async def parse(self) -> List[Gift]:
        pass

    @abstractmethod
    def get_platform_name(self) -> str:
        pass
