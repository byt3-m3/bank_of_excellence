from dataclasses import dataclass
from uuid import UUID
from serde import serialize, deserialize

@serialize
@deserialize
@dataclass
class Entity:
    id: UUID

@serialize
@deserialize
@dataclass(frozen=True)
class AppEvent:
    pass

@serialize
@deserialize
@dataclass(frozen=True)
class AppNotification:
    pass
