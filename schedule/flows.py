# pyright: reportGeneralTypeIssues=false
from typing import cast
from django.db import transaction
from schedule import utils


class AssignmentState:
    def __init__(self, instance) -> None:
        from schedule.models import Assignment
        self.instance = cast(Assignment,instance)

    def rescue(self):
        raise NotImplementedError(f'Status:{self.instance.get_status_display()}') # type: ignore

    def confirm(self):
        raise NotImplementedError(f'Status:{self.instance.get_status_display()}') # type: ignore

    def start(self):
        raise NotImplementedError(f'Status:{self.instance.get_status_display()}') # type: ignore

    def finish(self):
        raise NotImplementedError(f'Status:{self.instance.get_status_display()}') # type: ignore

    def migrate(self, start_slot, duration_slot, created_by):
        raise NotImplementedError(f'Status:{self.instance.get_status_display()}') # type: ignore

    def cancel(self):
        raise NotImplementedError(f'Status:{self.instance.get_status_display()}') # type: ignore

    def absent(self):
        raise NotImplementedError(f'Status:{self.instance.get_status_display()}') # type: ignore
        
    
class AssignmentStatePeding(AssignmentState):
    ## Esse estado é para que futuramente seja implementado um sistema de concorrencia
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
    def cancel(self):
        rules = utils.AssignmentUtil(self.instance)
        with transaction.atomic():
            rules.vacateTimeSlot()
            self.instance.status = self.instance.Status.CANCELLED.value # type: ignore
            self.instance.save(update_fields=['status'])

    def migrate(self, start_slot, duration_slot, created_by):
        from schedule.models import Assignment

        rules = utils.AssignmentUtil(self.instance)
        with transaction.atomic():
            rules.vacateTimeSlot()
            self.instance.status = self.instance.Status.CANCELLED.value # type: ignore
            self.instance.save(update_fields=['status'])

            new_assignment = Assignment.objects.create(
                date=self.instance.date,
                service=self.instance.service,
                start_slot=start_slot,
                duration_slot=duration_slot,
                status=self.instance.Status.MIGRATED.value,
                created_by=created_by,
            )
            new_assignment.resources.set(self.instance.resources.all())

            new_rules = utils.AssignmentUtil(new_assignment)
            new_rules.checkResourceOccupations()
            new_rules.occupyTimeSlot()

    def start(self):
        self.instance.status = self.instance.Status.IN_PROGRESS.value # type: ignore
        self.instance.save(update_fields=['status'])

    def absent(self):
        rules = utils.AssignmentUtil(self.instance)
        with transaction.atomic():
            rules.vacateTimeSlot()
            self.instance.status = self.instance.Status.ABSENT.value # type: ignore
            self.instance.save(update_fields=['status'])

            

class AssignmentStateMigrated(AssignmentStateConfirmed):
    pass # Mesmas ações do estado de Confirmado

class AssignmentStateInProgress(AssignmentState):
    def cancel(self):
        rules = utils.AssignmentUtil(self.instance)
        with transaction.atomic():
            rules.vacateTimeSlot()
            self.instance.status = self.instance.Status.CANCELLED.value # type: ignore
            self.instance.save(update_fields=['status'])

    def finish(self):
        self.instance.status = self.instance.Status.COMPLETED.value # type: ignore
        self.instance.save(update_fields=['status'])

class AssignmentStateCancelled(AssignmentState):
    def rescue(self):
        rules = utils.AssignmentUtil(self.instance)
        with transaction.atomic():
            rules.checkResourceOccupations()
            rules.occupyTimeSlot()
            self.instance.status = self.instance.Status.CONFIRMED.value # type: ignore
            self.instance.save(update_fields=['status'])

class AssignmentStateCompleted(AssignmentState):
    pass

class AssignmentStateAbsent(AssignmentState):
    pass

class NotStateError(Exception):
    pass
