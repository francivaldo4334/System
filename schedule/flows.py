class FlowState:
    def __init__(self, model) -> None:
        self.model = model

class FlowStateCreated(FlowState):
    pass

class FlowStateInProgress(FlowState):
    pass

class FlowStateCompleted(FlowState):
    pass

class FlowStateMigrated(FlowState):
    pass

class FlowStateCancelled(FlowState):
    pass

class NotStateError(Exception):
    pass
