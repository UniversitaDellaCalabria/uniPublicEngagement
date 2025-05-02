from django.contrib import messages
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.admin.utils import _get_changed_field_labels_from_form
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from organizational_area.models import *

from template.utils import *

from .. decorators.generic import *
from .. decorators.patronage import *
from .. forms import *
from .. models import *
from .. settings import *
from .. utils import *
from .. views import management


@login_required
@patronage_operator_structures
def dashboard(request, structures=None):
    template = 'patronage/dashboard.html'
    organizational_structures = OrganizationalStructure.objects.filter(pk__in=structures)
    breadcrumbs = {reverse('template:dashboard'): _('Dashboard'),
                   reverse('pe_management:dashboard'): _('Home'),
                   '#': _('Patronage operator')}

    active_years = PublicEngagementAnnualMonitoring.objects\
                                                   .filter(is_active=True)\
                                                   .values_list('year', flat=True)
    years_query = Q()
    for year in active_years:
        years_query |= Q(start__year=year)

    event_counts = PublicEngagementEvent.objects.filter(
        years_query,
        structure__pk__in=structures,
        data__patronage_requested=True,
        operator_evaluation_success=True,
        created_by_manager=False,
        is_active=True,
        start__gte=timezone.now()
    ).values("structure__id").annotate(
        to_handle_count=Count("id", filter=Q(patronage_operator_taken_date__isnull=True)),
        to_evaluate_count=Count("id", filter=Q(patronage_operator_taken_date__isnull=False, patronage_granted_date__isnull=True))
    )

    return render(request, template, {'breadcrumbs': breadcrumbs,
                                      'event_counts': event_counts,
                                      'structures': organizational_structures})


@login_required
@is_structure_patronage_operator
def events(request, structure_slug, structure=None):
    template = 'patronage/events.html'
    breadcrumbs = {reverse('template:dashboard'): _('Dashboard'),
                   reverse('pe_management:dashboard'): _('Home'),
                   reverse('pe_management:patronage_operator_dashboard'): _('Patronage operator'),
                   '#': structure.name}
    api_url = reverse('pe_management:api_patronage_operator_events', kwargs={'structure_slug': structure_slug})
    return render(request, template, {'breadcrumbs': breadcrumbs,
                                      'api_url': api_url,
                                      'structure_slug': structure_slug})


@login_required
@is_structure_patronage_operator
def event(request, structure_slug, event_id, structure=None):
    event = PublicEngagementEvent.objects.prefetch_related('data')\
                                         .filter(pk=event_id,
                                                 structure__slug=structure_slug,
                                                 data__patronage_requested=True).first()
    if not event:
        messages.add_message(request, messages.ERROR,
                             "<b>{}</b>: {}".format(_('Alert'), _('URL access is not allowed')))
        return redirect('pe_management:patronage_operator_events', structure_slug=structure_slug)

    breadcrumbs = {reverse('template:dashboard'): _('Dashboard'),
                   reverse('pe_management:dashboard'): _('Home'),
                   reverse('pe_management:patronage_operator_dashboard'): _('Patronage operator'),
                   reverse('pe_management:patronage_operator_events', kwargs={'structure_slug': structure_slug}): structure.name,
                   '#': event.title}
    template = 'patronage/event.html'

    logs = LogEntry.objects.filter(content_type_id=ContentType.objects.get_for_model(event).pk,
                                   object_id=event.pk)

    return render(request, template, {'breadcrumbs': breadcrumbs,
                                      'event': event,
                                      'logs': logs,
                                      'structure_slug': structure_slug})


@login_required
@require_POST
@is_structure_patronage_operator
def take_event(request, structure_slug, event_id, structure=None):
    event = PublicEngagementEvent.objects.prefetch_related('data')\
                                         .filter(pk=event_id,
                                                 structure__slug=structure_slug,
                                                 data__patronage_requested=True).first()

    if not event:
        messages.add_message(request, messages.ERROR, _("Access denied"))
        return redirect('pe_management:patronage_operator_events',
                        structure_slug=structure_slug)
    if not event.can_be_handled_for_patronage():
        messages.add_message(request, messages.ERROR, _("Access denied"))
        return redirect('pe_management:patronage_operator_event',
                        structure_slug=structure_slug,
                        event_id=event_id)

    event.patronage_operator_taken_by = request.user
    event.patronage_operator_taken_date = timezone.now()
    event.modified_by = request.user
    event.save()

    log_action(user=request.user,
               obj=event,
               flag=CHANGE,
               msg="[Patrocinio {}] Iniziativa presa in carico".format(structure_slug))

    messages.add_message(request, messages.SUCCESS,
                         _("Event taken successfully"))

    # invia email al referente/compilatore
    subject = '{} - "{}" - {}'.format(_('Public engagement'), event.title, _('Handled'))
    body = "{} {} {}".format(request.user, _('is evaluating the event'), '.')
    send_email_to_event_referents(event, subject, body)

    return redirect('pe_management:patronage_operator_event',
                    structure_slug=structure_slug,
                    event_id=event_id)


@login_required
@is_structure_patronage_operator
def event_evaluation(request, structure_slug, event_id, structure=None):
    event = PublicEngagementEvent.objects.prefetch_related('data')\
                                         .filter(pk=event_id,
                                                 structure__slug=structure_slug,
                                                 data__patronage_requested=True).first()

    if not event:
        messages.add_message(request, messages.ERROR, _("Access denied"))
        return redirect('pe_management:patronage_operator_events',
                        structure_slug=structure_slug)

    if not event.is_ready_for_patronage_check():
        messages.add_message(request, messages.ERROR, _("Access denied"))
        return redirect('pe_management:patronage_operator_event',
                        structure_slug=structure_slug,
                        event_id=event_id)

    form = PublicEngagementEventEvaluationForm()
    template = 'event_evaluation.html'
    breadcrumbs = {reverse('template:dashboard'): _('Dashboard'),
                   reverse('pe_management:dashboard'): _('Home'),
                   reverse('pe_management:patronage_operator_dashboard'): _('Patronage operator'),
                   reverse('pe_management:patronage_operator_events', kwargs={'structure_slug': structure_slug}): structure.name,
                   reverse('pe_management:patronage_operator_event', kwargs={'structure_slug': structure_slug, 'event_id': event_id}): '{}'.format(event.title),
                   '#': _('Evaluation')}

    if request.method == 'POST':
        form = PublicEngagementEventEvaluationForm(data=request.POST)
        if form.is_valid():
            event.patronage_granted_date = timezone.now()
            event.patronage_granted = form.cleaned_data['success']
            event.patronage_granted_by = request.user
            event.patronage_granted_notes = form.cleaned_data['notes']
            event.modified_by = request.user
            event.save()

            messages.add_message(request, messages.SUCCESS, _("Patronage evaluation completed"))

            log_result = "concesso" if form.cleaned_data['success'] == 'True' else "negato"
            msg = "[Patrocinio {}] Esito valutazione: {}".format(structure_slug, log_result)
            if not form.cleaned_data['success'] == 'True':
                msg += ' {}'.format(event.patronage_granted_notes)

            log_action(user=request.user,
                       obj=event,
                       flag=CHANGE,
                       msg=msg)

            # invia email al referente/compilatore
            result = _('approved') if form.cleaned_data['success'] == 'True' else _('not approved')
            subject = '{} - "{}" - {}'.format(_('Public engagement'), event.title, _('Patronage evaluation completed'))
            body = "{} {}: {}.".format(request.user, _('has evaluated the event with the result'), result)
            if not form.cleaned_data['success'] == 'True':
                body += '\n{}: {}'.format(_('Notes'), form.cleaned_data['notes'])
            send_email_to_event_referents(event, subject, body)

            # invia email ai manager
            send_email_to_managers(subject, body)

            return redirect("pe_management:patronage_operator_event",
                            structure_slug=structure_slug,
                            event_id=event_id)
        else:
            messages.add_message(request, messages.ERROR,
                                 "<b>{}</b>: {}".format(_('Alert'), _('the errors in the form below need to be fixed')))
    return render(request, template, {'event': event, 'form': form, 'structure_slug': structure_slug})


@login_required
@require_POST
@is_structure_patronage_operator
def event_reopen_evaluation(request, structure_slug, event_id, structure=None):
    event = PublicEngagementEvent.objects.prefetch_related('data')\
                                         .filter(pk=event_id,
                                                 structure__slug=structure_slug,
                                                 data__patronage_requested=True).first()
    if not event:
        messages.add_message(request, messages.ERROR, _("Access denied"))
        return redirect('pe_management:patronage_operator_events',
                        structure_slug=structure_slug)

    if not event.patronage_can_be_reviewed():
        messages.add_message(request, messages.ERROR, _("Access denied"))
        return redirect('pe_management:patronage_operator_event',
                        structure_slug=structure_slug,
                        event_id=event_id)

    event.patronage_granted_date = None
    event.modified_by = request.user
    event.save()

    log_action(user=request.user,
               obj=event,
               flag=CHANGE,
               msg="[Patrocinio {}] Valutazione riaperta".format(structure_slug))

    messages.add_message(request, messages.SUCCESS, _("Evaluation reopened"))

    # email
    subject = '{} - "{}" - {}'.format(_('Public engagement'), event.title, _('Patronage evaluation reopened'))
    body = "{} {} {}".format(request.user, _('has reopened patronage evaluation of the event'), '.')
    send_email_to_event_referents(event, subject, body)

    # invia email ai manager
    if event.patronage_granted:
        send_email_to_managers(subject, body)

    return redirect("pe_management:patronage_operator_event",
                    structure_slug=structure_slug,
                    event_id=event_id)
