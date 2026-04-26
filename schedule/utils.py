# pyright: reportAssignmentType=false
# pyright: reportAttributeAccessIssue=false
# pyright: reportArgumentType=false
# Exceptions

from typing import List, cast


class ResourceNotAllowed(Exception):
    pass

class ReourceQuantityNotEguals(Exception):
    pass

class ResourceOcuppied(Exception):
    pass

class ServiceIsRequired(Exception):
    pass
# Utils
class AssignmentUtil:
    def __init__(self, assigment) -> None:
        from schedule.models import Assignment
        self.assignment = cast(Assignment,assigment);

    def checkServiceRequirements(self):
        from schedule.models import Service, ServiceResourceRelation, ResourceSelectable

        if not isinstance(self.assignment.service, Service):
            raise ServiceIsRequired();

        service: Service = self.assignment.service
        service_requirements: List[ServiceResourceRelation] = list(ServiceResourceRelation.objects.filter(service=service))
        resources:List[ResourceSelectable] = list(self.assignment.resources.all())
        for service_requirement in service_requirements:
            resource_count = len([it for it in resources if it.parent_id == service_requirement.resource_type_id])
            if resource_count != service_requirement.quantity:
                raise ReourceQuantityNotEguals()

        total_required_resources = sum([it.quantity for it in service_requirements]);
        total_resources = len(resources)

        if total_required_resources  != total_resources:
            raise ResourceNotAllowed()
        
    def checkResourceOccupations(self):
        from schedule.models import ResourceSelectable, ResourceOccupation

        resources:List[ResourceSelectable] = list(self.assignment.resources.all())

        for resource in resources:
            occupation, _ = ResourceOccupation.objects.get_or_create(
                resource=resource,
                date=self.assignment.date,
            )
            occupation_queryset:ResourceOccupation.QuerySet = ResourceOccupation.objects.filter(pk=occupation.pk)
            occupation_queryset.select_for_update()
            is_available = occupation_queryset.available(
                start_slot=self.assignment.start_slot,
                duration_slot=self.assignment.duration_slot
            ).exists()
            if not is_available:
                raise ResourceOcuppied()

    def occupyTimeSlot(self):
        from schedule.models import ResourceOccupation
        occupation_queryset:ResourceOccupation.QuerySet = ResourceOccupation.objects.all()
        occupation_queryset.occupy(
            start_slot=self.assignment.start_slot,
            duration_slot=self.assignment.duration_slot,
        )

    def vacateTimeSlot(self):
        from schedule.models import ResourceOccupation
        occupation_queryset:ResourceOccupation.QuerySet = ResourceOccupation.objects.all()
        occupation_queryset.vacate(
            start_slot=self.assignment.start_slot,
            duration_slot=self.assignment.duration_slot,
        )
