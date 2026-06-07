
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

    def choice_random(self, parent_resources):
        import random
        from schedule.models import ResourceSelectable

        results = []
    
        for req in parent_resources:
            candidates = list(ResourceSelectable.objects.filter(parent=req.resource_type))
        
            if not candidates:
                raise ResourceNotAllowed(req.resource_type)
            for _ in range(req.quantity):
                results.append(random.choice(candidates))
            
        return results
    def checkServiceRequirements(self):
        from schedule.models import Service, ServiceResourceRelation, Resource
        if not isinstance(self.assignment.service, Service):
            raise ServiceIsRequired()

        service: Service = self.assignment.service

        requirements = list(
            ServiceResourceRelation.objects.filter(service=service)
            .select_related('resource_type')
        )

        # 1. Separação correta dos requisitos do serviço
        req_required = [r for r in requirements if r.resource_type.choice_type == Resource.ChoiceType.REQUIRED_FOR_CLIENT.value]
        req_optional = [r for r in requirements if r.resource_type.choice_type == Resource.ChoiceType.OPTIONAL_FOR_CLIENT.value]
        req_internal = [r for r in requirements if r.resource_type.choice_type == Resource.ChoiceType.INVISIBLE_FOR_CLIENT.value]

        # Recursos atuais que já estão associados ao agendamento
        current_choiced = list(self.assignment.resources.all().select_related('parent'))

        # Validação: Garante que nenhum recurso fora dos requisitos foi adicionado
        allowed_parents = {req.resource_type_id for req in requirements}
        if any(r.parent_id not in allowed_parents for r in current_choiced):
            raise ResourceNotAllowed()

        # 2. Separação dos recursos já escolhidos pelo cliente/sistema
        choiced_required = [r for r in current_choiced if r.parent.choice_type == Resource.ChoiceType.REQUIRED_FOR_CLIENT.value]
        choiced_optional = [r for r in current_choiced if r.parent.choice_type == Resource.ChoiceType.OPTIONAL_FOR_CLIENT.value]
        choiced_internal = [r for r in current_choiced if r.parent.choice_type == Resource.ChoiceType.INVISIBLE_FOR_CLIENT.value]

        # 3. Validação e Preenchimento: OBRIGATÓRIOS
        # Soma as quantidades exigidas pelas regras
        total_required_qty = sum(req.quantity for req in req_required)
        if len(choiced_required) != total_required_qty:
            raise ReourceQuantityNotEguals()

        # 4. Validação e Preenchimento: OPCIONAIS
        total_optional_qty = sum(req.quantity for req in req_optional)
        if len(choiced_optional) > total_optional_qty:
            raise ResourceNotAllowed()
    
        if len(choiced_optional) < total_optional_qty:
            # Identifica quais requisitos opcionais ainda não foram preenchidos
            filled_parent_pks = [r.parent_id for r in choiced_optional]
            to_choice = [req for req in req_optional if req.resource_type_id not in filled_parent_pks]
    
            # Completa o restante aleatoriamente
            choiced_optional += self.choice_random(to_choice)

        # 5. Validação e Preenchimento: INVISÍVEIS (INTERNOS)
        total_internal_qty = sum(req.quantity for req in req_internal)
        if len(choiced_internal) > total_internal_qty:
            raise ResourceNotAllowed()
    
        if len(choiced_internal) < total_internal_qty:
            filled_parent_pks = [r.parent_id for r in choiced_internal]
            to_choice = [req for req in req_internal if req.resource_type_id not in filled_parent_pks]
    
            choiced_internal += self.choice_random(to_choice)

        # 6. Consolidação e Salvamento
        all_resources_choiced = choiced_required + choiced_optional + choiced_internal
        total_expected_resources = total_required_qty + total_optional_qty + total_internal_qty

        if len(all_resources_choiced) != total_expected_resources:
            raise ResourceNotAllowed(f'{total_expected_resources}/{len(all_resources_choiced)}')

        # Salva os recursos de fato no relacionamento ManyToMany
        if all_resources_choiced:
            self.assignment.resources.set(all_resources_choiced)

        # resources_to_add = []
        # total_auto_expected = 0

        # self.set_sistem_auto_choice_resource(
        #         auto_choice_resources,
        #         total_auto_expected,
        #         resources_to_add,
        # )
        # # Pegando os recursos que o cliente já selecionou
        # current_resources = list(self.assignment.resources.all())
        # current_resources_optionals = [it for it in current_resources if it.parent.choice_type == Resource.ChoiceType.OPTIONAL_FOR_CLIENT.value]
    
        # # 2. CORREÇÃO: A lista provisória DEVE conter os atuais + os automáticos gerados
        # all_resources_provisional = current_resources + resources_to_add

        # # 3. Validando as quantidades por tipo de recurso (manuais e automáticos)
        # for req in requirements:
        #     resource_count = sum(1 for it in all_resources_provisional if it.parent_id == req.resource_type_id)
        #     if resource_count != req.quantity:
        #         raise ReourceQuantityNotEguals() # Atenção ao typo original do seu código

        # # 4. Validando o total geral esperado
        # total_required_resources = sum(it.quantity for it in service_requirements)
        # total_expected = total_required_resources + total_auto_expected

        # if len(all_resources_provisional) != total_expected:
        #     raise ResourceNotAllowed(f'{len(all_resources_provisional)}/{total_expected}')

        # # 5. Salva no banco apenas se todas as validações passarem
        # if resources_to_add:
        #     self.assignment.resources.add(*resources_to_add)
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
        for resource in list(self.assignment.resources.all()):
            resource = cast(Resource, resource)
            occupation_queryset = ResourceOccupation.objects.filter(
                date=self.assignment.date,
                resource=resource,
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
def time_to_slots(t: datetime.time) -> int:
    total_minutes = t.hour * 60 + t.minute
    return total_minutes // 5
