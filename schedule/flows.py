# pyright: reportGeneralTypeIssues=false
from django.db import transaction
from schedule import utils


class AssignmentState:
    from schedule.models import Assignment
    def __init__(self, instance:Assignment) -> None:
        self.instance = instance

    def confirm(self):
        raise NotImplementedError(f'Status:{self.instance.get_status_display()}') # type: ignore

    def start(self):
        raise NotImplementedError(f'Status:{self.instance.get_status_display()}') # type: ignore

    def finish(self):
        raise NotImplementedError(f'Status:{self.instance.get_status_display()}') # type: ignore

    def migrate(self, star_slot, duration_slot):
        raise NotImplementedError(f'Status:{self.instance.get_status_display()}') # type: ignore

    def cancel(self):
        raise NotImplementedError(f'Status:{self.instance.get_status_display()}') # type: ignore
    
class AssignmentStatePeding(AssignmentState):
    def confirm(self):
        with transaction.atomic():
            rules = utils.AssignmentUtil(self.instance)
            try:
                rules.checkServiceRequirements()
            except utils.ServiceIsRequired:
                rules.checkResourceOccupations()
            except Exception as e:
                raise e
            rules.occupyTimeSlot()
            self.instance.status = self.instance.Status.CONFIRMED.value # type: ignore
            self.instance.save()
            
class AssignmentStateConfirmed(AssignmentState):
    pass

class AssignmentStateInProgress(AssignmentState):
    pass

class AssignmentStateCompleted(AssignmentState):
    pass

class AssignmentStateMigrated(AssignmentState):
    pass

class AssignmentStateCancelled(AssignmentState):
    pass

class NotStateError(Exception):
    pass
