from django.conf import settings
from django.utils import timezone


PE_EVENTS_YEAR_TO_SHOW = getattr(settings, "PE_EVENTS_YEAR_TO_SHOW", timezone.localtime().year)
