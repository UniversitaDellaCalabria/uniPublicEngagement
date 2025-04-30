from django import template

from .. models import PublicEngagementAnnualMonitoring
from .. import settings

register = template.Library()


@register.simple_tag
def pem_settings_value(name, **kwargs):
    value = getattr(settings, name, None)
    if value and kwargs:
        return value.format(**kwargs)
    return value

@register.simple_tag
def get_field_label(model, field_name):
    return model.__class__.__dict__[field_name].field.verbose_name

@register.simple_tag
def filter_events_per_structure_id(events, sid):
    return events.filter(structure__id=sid)
