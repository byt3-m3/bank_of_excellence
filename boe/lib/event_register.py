from dataclasses import dataclass
from typing import Dict


@dataclass
class EventHandlerMapping:
    event_handler: callable
    event_factory_func: callable
    event_class: type


class EventMapRegister:

    def __init__(self):
        self.event_map: Dict[str, EventHandlerMapping] = {}

    def register_event(
            self,
            event_name: str,
            event_class: type,
            event_handler: callable,
            event_factory_func: callable
    ):
        self.event_map[event_name] = EventHandlerMapping(
            event_class=event_class,
            event_handler=event_handler,
            event_factory_func=event_factory_func
        )

    def get_event_mapping(self, event_name: str) -> EventHandlerMapping:
        return self.event_map.get(event_name)

    def get_event_factory(self, event_name) -> callable:
        _mapping = self.get_event_mapping(event_name=event_name)
        return _mapping.event_factory_func

    def get_event_handler(self, event_name) -> callable:
        _mapping = self.get_event_mapping(event_name=event_name)
        return _mapping.event_handler

    def get_event_class(self, event_name) -> type:
        _mapping = self.get_event_mapping(event_name=event_name)
        return _mapping.event_class
