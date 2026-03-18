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
