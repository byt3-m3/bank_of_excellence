from dataclasses import dataclass
from uuid import UUID


@dataclass
class Entity:
    id: UUID


@dataclass(frozen=True)
class AppEvent:
    pass
