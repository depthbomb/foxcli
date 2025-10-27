from typing import Optional
from dataclasses import dataclass

@dataclass
class CommandInfo:
    name: str
    description: str
    aliases: list[str]
    doc: Optional[str]
