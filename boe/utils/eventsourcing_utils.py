from eventsourcing.domain import Snapshot


def make_snapshot(aggregate):
    snapshot = Snapshot.take(aggregate=aggregate)
    return snapshot.mutate(None)
