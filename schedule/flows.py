# pyright: reportGeneralTypeIssues=false
from collections import Counter
from django.db import transaction
from django.db.models import QuerySet
from typing import List, cast


class AssignmentState:
    def __init__(self, instance) -> None:
        from schedule.models import Assignment
        self.instance = cast(Assignment, instance)

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
    class ResourceNotAllowed(Exception):
        pass
    class ReourceQuantityNotEguals(Exception):
        pass
    class ResourceOcuppied(Exception):
        pass

    def confirm(self):
        from schedule.models import ResourceOccupation, Resource, Service, ServiceResourceRelation

        with transaction.atomic():
            # 1. Validação
            # 1.1 Carrega variaveis para validação
            service = cast(Service,self.instance.service)
            service_resource_relation_qs = cast(QuerySet, getattr(ServiceResourceRelation, 'objects'))
            service_resource_relation_resource_type_id_and_quantity = \
                service_resource_relation_qs.filter(service=service).values_list('resource_type_id', 'quantity')
            service_required_resource_quantity_map = dict(service_resource_relation_resource_type_id_and_quantity)
            instance_resource_qs = cast(QuerySet, self.instance.resources)
            instance_resource_paret_id_and_id = list(instance_resource_qs.values('parent_id', 'id'))
            instance_resource_ids = [it['id'] for it in instance_resource_paret_id_and_id]
            resource_occupation_qs = cast(ResourceOccupation.QuerySet, ResourceOccupation.objects)
            instance_resource_parent_id_quantity_map = Counter([it['parent_id'] for it in instance_resource_paret_id_and_id])
            # 1.2 validar resources requiridos de acordo com o tipo de resource do serviço
            print(instance_resource_parent_id_quantity_map, service_required_resource_quantity_map)
            for id, qty in service_required_resource_quantity_map.items():
                if id not in instance_resource_parent_id_quantity_map.keys():
                    raise self.ResourceNotAllowed()
                if qty != \
                   instance_resource_parent_id_quantity_map[id]:
                    raise self.ReourceQuantityNotEguals()
            # 2. Obter a ocupações dos resource usados
            for resource_id in instance_resource_ids:
                occupation, _ = resource_occupation_qs.get_or_create(
                    resource_id=resource_id,
                    date=self.instance.date,
                )
            # 2.1 Verifica se todas as ocupações usadas tem disponibilidade
                occ_qs = resource_occupation_qs.filter(pk=getattr(occupation, 'pk')).select_for_update()
                if not occ_qs.available(self.instance.start_slot,
                                                       self.instance.duration_slot).exists():
                    raise self.ResourceOcuppied()
            # 2.2 Atualiza a ocupação do resource usado
                occ_qs.occupy(self.instance.start_slot, self.instance.duration_slot)
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
