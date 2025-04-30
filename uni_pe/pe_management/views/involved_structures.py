from django.contrib import messages
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.admin.utils import _get_changed_field_labels_from_form
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from organizational_area.models import *

from template.utils import *

from .. decorators.generic import *
from .. decorators.operator import *
from .. forms import *
from .. models import *
from .. settings import *
from .. utils import *
from .. views import management


@login_required
@evaluation_operator_structures
def dashboard(request, structures=None):
    template = 'operator/involved-structures/dashboard.html'
    organizational_structures = OrganizationalStructure.objects.filter(pk__in=structures)

    breadcrumbs = {reverse('template:dashboard'): _('Dashboard'),
                   reverse('pe_management:dashboard'): _('Public engagement'),
                   '#': _('Involved structure operator')}

    return render(request, template, {'breadcrumbs': breadcrumbs,
                                      'structures': organizational_structures})


@login_required
@is_structure_evaluation_operator
def events(request, structure_slug, structure=None):
    template = 'operator/involved-structures/events.html'
    breadcrumbs = {reverse('template:dashboard'): _('Dashboard'),
                   reverse('pe_management:dashboard'): _('Public engagement'),
                   reverse('pe_management:operator_dashboard'): _('Involved structure operator'),
                   '#': structure.name}
    api_url = reverse('pe_management:api_involved_structures_events', kwargs={'structure_slug': structure_slug})
    return render(request, template, {'breadcrumbs': breadcrumbs,
                                      'api_url': api_url,
                                      'structure_slug': structure_slug})


@login_required
@is_structure_evaluation_operator
def event(request, structure_slug, event_id, structure=None):
    event = PublicEngagementEvent.objects.filter(pk=event_id,
                                                 data__involved_structure__slug=structure_slug).first()
    if not event or not event.data or not event.operator_evaluation_date:
        messages.add_message(request, messages.ERROR,
                             "<b>{}</b>: {}".format(_('Alert'), _('URL access is not allowed')))
        return redirect('pe_management:involved_structures_events', structure_slug=structure_slug)

    breadcrumbs = {reverse('template:dashboard'): _('Dashboard'),
                   reverse('pe_management:dashboard'): _('Public engagement'),
                   reverse('pe_management:operator_dashboard'): _('Involved structure operator'),
                   reverse('pe_management:operator_events', kwargs={'structure_slug': structure_slug}): structure.name,
                   '#': event.title}
    template = 'operator/involved-structures/event.html'

    logs = LogEntry.objects.filter(content_type_id=ContentType.objects.get_for_model(event).pk,
                                   object_id=event.pk)

    return render(request, template, {'breadcrumbs': breadcrumbs,
                                      'event': event,
                                      'logs': logs,
                                      'structure_slug': structure_slug})
