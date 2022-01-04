import datetime
from uuid import UUID

from boe.applications.task_domain_apps import TaskDomainAppEventFactory
from boe.clients.client import PikaPublisherClient
from boe.env import BOE_APP_EXCHANGE, TASK_MANAGER_QUEUE_ROUTING_KEY


class TaskManagerWorkerClient(PikaPublisherClient):

    def __init__(self):
        super().__init__(

            BOE_APP_EXCHANGE,
            TASK_MANAGER_QUEUE_ROUTING_KEY,

        )
        self.event_factory = TaskDomainAppEventFactory()

    def publish_new_task_event(
            self,
            name: str,
            description: str,
            due_date: datetime.datetime,
            owner_id: UUID,
            evidence_required: bool,
            value: float

    ):
        event = self.event_factory.build_new_task_event(
            description=description,
            due_date=due_date,
            owner_id=str(owner_id),
            evidence_required=evidence_required,
            value=value,
            name=name
        )
        print(event)
        self.publish_event(event=event)