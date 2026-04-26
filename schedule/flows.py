# pyright: reportGeneralTypeIssues=false
from typing import cast
from django.db import transaction
from schedule import utils


class AssignmentState:
    def __init__(self, instance) -> None:
        from schedule.models import Assignment
        self.instance = cast(Assignment,instance)

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
        rules = utils.AssignmentUtil(self.instance)
        with transaction.atomic():
            try:
                rules.checkServiceRequirements()
            except utils.ServiceIsRequired:
                pass
            rules.checkResourceOccupations()
            rules.occupyTimeSlot()
            self.instance.status = self.instance.Status.CONFIRMED.value # type: ignore
            self.instance.save(update_fields=['status'])
    def cancel(self):
        #Caso seja cancelado antes de confirmar ele é deletado
        self.instance.delete()
            
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
