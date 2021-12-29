from boe.lib.event_register import EventMapRegister


def register_event_map(event_map_register: EventMapRegister, event_map: dict):
    for event_name, event_options in event_map.items():
        event_map_register.register_event(
            event_name=event_name,
            event_handler=event_options['event_handler'],
            event_factory_func=event_options['event_factory'],
            event_class=event_options['event_class'],
        )
