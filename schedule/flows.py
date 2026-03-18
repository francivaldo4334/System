# pyright: reportGeneralTypeIssues=false
from django.db import transaction


class AssignmentSlotState:
    def __init__(self, instance) -> None:
        from typing import cast
        from schedule.models import AssignmentSlot
        self.instance = cast(AssignmentSlot, instance)

    def occupy(self):
        raise NotImplementedError()

    def vacate(self):
        raise NotImplementedError()

class AssignmentSlotStateCreated(AssignmentSlotState):
    def occupy(self):
        from schedule.models import ResourceOccupation
        with transaction.atomic():
            self.instance.save()

            pass

class AssignmentSlotStateInProgress(AssignmentSlotState):
    pass

class AssignmentSlotStateCompleted(AssignmentSlotState):
    pass

class AssignmentSlotStateMigrated(AssignmentSlotState):
    pass

class AssignmentSlotStateCancelled(AssignmentSlotState):
    pass

class NotStateError(Exception):
    pass
