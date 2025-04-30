import requests

from copy import deepcopy

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.admin.utils import _get_changed_field_labels_from_form
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, redirect, reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from organizational_area.models import *
from organizational_area.utils import user_in_office

from template.utils import *

from .. decorators.generic import *
from .. decorators.user import *
from .. forms import *
from .. models import *
from .. settings import *
from .. utils import *


@login_required
@can_manage_public_engagement
def events(request):
    template = 'involved_personnel/events.html'
    breadcrumbs = {reverse('template:dashboard'): _('Dashboard'),
                   reverse('pe_management:dashboard'): _('Public engagement'),
                   '#': _('Other involved personnel events')}
    api_url = reverse('pe_management:api_involved_personnel_events')
    return render(request, template, {'breadcrumbs': breadcrumbs,
                                      'api_url': api_url})


@login_required
@has_access_to_my_event
def event(request, event_id, event=None):
    template = 'involved_personnel/event.html'
    breadcrumbs = {reverse('template:dashboard'): _('Dashboard'),
                   reverse('pe_management:dashboard'): _('Public engagement'),
                   reverse('pe_management:involved_personnel_events'): _('Other involved personnel events'),
                   '#': event.title}

    logs = LogEntry.objects.filter(content_type_id=ContentType.objects.get_for_model(event).pk,
                                   object_id=event.pk)

    return render(request, template, {'breadcrumbs': breadcrumbs,
                                      'event': event,
                                      'logs': logs})
