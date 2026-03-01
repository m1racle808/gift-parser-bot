from .base import BaseParser
from models import Gift
from typing import List

class PortalParser(BaseParser):
    def get_platform_name(self) -> str:
        return "portal"

    async def parse(self) -> List[Gift]:
        print("Portal парсер пока не реализован")
        return []
