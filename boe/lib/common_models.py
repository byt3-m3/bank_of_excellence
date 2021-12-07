from dataclasses import dataclass
from uuid import UUID


@dataclass
class Aggregate:
    id: UUID


@dataclass(frozen=True)
class AppEvent:
    pass
