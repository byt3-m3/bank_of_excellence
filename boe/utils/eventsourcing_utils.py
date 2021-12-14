from eventsourcing.domain import Snapshot


def make_snapshot(aggregate):
    return Snapshot.take(aggregate=aggregate)
