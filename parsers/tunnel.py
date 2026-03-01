from .base import BaseParser
from models import Gift
from typing import List

class TunnelParser(BaseParser):
    def get_platform_name(self) -> str:
        return "tunnel"

    async def parse(self) -> List[Gift]:
        print("Tunnel парсер пока не реализован")
        return []
