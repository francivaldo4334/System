class FlowState:
    def __init__(self, instance) -> None:
        self.instance = instance

class AssignmentSlotStateCreated(FlowState):
    pass

class AssignmentSlotStateInProgress(FlowState):
    pass

class AssignmentSlotStateCompleted(FlowState):
    pass

class AssignmentSlotStateMigrated(FlowState):
    pass

class AssignmentSlotStateCancelled(FlowState):
    pass

class NotStateError(Exception):
    pass
