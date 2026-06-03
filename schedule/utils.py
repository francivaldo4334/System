
import datetime
from typing import List, cast

from django_filters import DateTimeFilter


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
            from schedule.models import Service, ServiceResourceRelation, ResourceSelectable, Resource

            if not isinstance(self.assignment.service, Service):
                raise ServiceIsRequired()

            service: Service = self.assignment.service
            requirements = ServiceResourceRelation.objects.filter(service=service)
            service_requirements = [r for r in requirements if not r.resource_type.is_auto_choice]
            auto_choice_resources = [r for r in requirements if r.resource_type.is_auto_choice]

            resources_to_add = []
            for r in auto_choice_resources:
                s_r = ResourceSelectable.objects.filter(parent=r.resource_type).order_by('?').first()
                if not s_r:
                    raise ResourceNotAllowed()
            
                resources_to_add.append(s_r)

            current_resources = list(self.assignment.resources.all())
            all_resources_provisional = current_resources

            for req in service_requirements:
                resource_count = sum(1 for it in all_resources_provisional if it.parent_id == req.resource_type_id)
                if resource_count != req.quantity:
                    raise ReourceQuantityNotEguals()

            total_required_resources = sum(it.quantity for it in service_requirements)
            total_expected = total_required_resources + len(auto_choice_resources) 

            if len(all_resources_provisional) != total_expected:
                raise ResourceNotAllowed()

            if resources_to_add:
                self.assignment.resources.add(*resources_to_add)        

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
        from schedule.models import ResourceOccupation, Resource
        for resource in self.assignment.resources.all():
            resource = cast(Resource, resource)
            occupation_queryset:ResourceOccupation.QuerySet = resource.resourceoccupation_set.filter(
                date=self.assignment.date
            )
            occupation_queryset.occupy(
                start_slot=self.assignment.start_slot,
                duration_slot=self.assignment.duration_slot,
            )

    def vacateTimeSlot(self):
        from schedule.models import ResourceOccupation, Resource
        for resource in self.assignment.resources.all():
            resource = cast(Resource, resource)
            occupation_queryset:ResourceOccupation.QuerySet = resource.resourceoccupation_set.filter(
                date=self.assignment.date
            )
            occupation_queryset.vacate(
                start_slot=self.assignment.start_slot,
                duration_slot=self.assignment.duration_slot,
            )

def slot_to_time(slot: int) -> datetime.time:
    total_minutes = slot * 5
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return datetime.time(hours, minutes)
