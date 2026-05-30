# pyright:reportAttributeAccessIssue=false
from typing import cast
from schedule.models import Assignment, Service
from datetime import datetime, time, timedelta
from urllib.parse import urlencode
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import zoneinfo


class LinkGenerator:
    def get_google_calendar_link(
        self,
        assignment: Assignment
    ):
        SLOT_DURATION_MINUTES = 5

        start_slot = cast(int,assignment.start_slot)
        duration_slot = cast(int,assignment.duration_slot)
        minutes_start = start_slot * SLOT_DURATION_MINUTES
        assignment_date = cast(datetime,assignment.date)

        start_time = (
            datetime.combine(
                assignment_date, time.min
            ) + timedelta(minutes=minutes_start)
        ).time()
        
        minutes_duration = duration_slot * SLOT_DURATION_MINUTES
        
        local_start_dt = datetime.combine(assignment_date, start_time)
        local_end_dt = local_start_dt + timedelta(minutes=minutes_duration)
        
        try:
            local_tz = zoneinfo.ZoneInfo(settings.TIME_ZONE)
        except Exception:
            local_tz = zoneinfo.ZoneInfo("America/Sao_Paulo") # Fallback seguro para o Brasil
            
        utc_start_dt = local_start_dt.replace(tzinfo=local_tz).astimezone(zoneinfo.ZoneInfo("UTC"))
        utc_end_dt = local_end_dt.replace(tzinfo=local_tz).astimezone(zoneinfo.ZoneInfo("UTC"))
        
        # 5. Formatar as datas no padrão que o Google exige: YYYYMMDDTHMMSSZ
        dates_param = f"{utc_start_dt.strftime('%Y%m%dT%H%M%SZ')}/{utc_end_dt.strftime('%Y%m%dT%H%M%SZ')}"
        
        # 6. Montar os textos de exibição (Título e Descrição)
        service = cast(Service, assignment.service)
        title = f"{service.title if service else _('Assignment')}"
        
        # Coleta os recursos vinculados, se houver (Tratamento de ManyToMany)
        # Nota: Só funciona perfeitamente se o objeto já estiver salvo no banco
        resources_str = ", ".join([str(r.name) for r in assignment.resources.all()]) if assignment.pk else ""
        
        details = f"{_('Status')}: {getattr(assignment,'get_status_display')()}\n"
        if resources_str:
            details += f"{_('Resources')}: {resources_str}\n"
        details += f"ID: {assignment.uuid}"

        # 7. Construir a URL com encode correto para evitar quebra de caracteres
        base_url = "https://calendar.google.com/calendar/render"
        query_params = {
            "action": "TEMPLATE",
            "text": title,
            "dates": dates_param,
            "details": details,
        }
        
        return f"{base_url}?{urlencode(query_params)}"
