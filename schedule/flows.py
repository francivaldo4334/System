class FlowState:
    def __init__(self, model) -> None:
        self.model = model

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
