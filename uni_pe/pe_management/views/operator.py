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

from itertools import chain

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
    template = 'operator/dashboard.html'
    organizational_structures = OrganizationalStructure.objects.filter(pk__in=structures)

    breadcrumbs = {
                   reverse('pe_management:dashboard'): _('Home'),
                   '#': _('Structure operator')}

    active_years = PublicEngagementAnnualMonitoring.objects\
                                                   .filter(is_active=True)\
                                                   .values_list('year', flat=True)
    years_query = Q()
    for year in active_years:
        years_query |= Q(start__year=year)

    event_counts = PublicEngagementEvent.objects.filter(
        structure__pk__in=structures,
        to_evaluate=True,
        created_by_manager=False,
    ).values("structure__id").annotate(
        to_handle_count=Count(
            "id",
            filter=Q(
                years_query,
                is_active=True,
                operator_taken_date__isnull=True
            )
        ),
        to_evaluate_count=Count(
            "id",
            filter=Q(
                years_query,
                is_active=True,
                operator_taken_date__isnull=False,
                operator_evaluation_date__isnull=True
            )
        ),
        approved_count=Count(
            "id",
            filter=Q(
                years_query,
                is_active=True,
                operator_evaluation_success=True,
                operator_evaluation_date__isnull=False
            )
        ),
        rejected_count=Count(
            "id",
            filter=Q(
                years_query
            ) & (
                Q(is_active=False) | Q(
                    operator_evaluation_success=False,
                    operator_evaluation_date__isnull=False
                )
            )
        ),
        total_approved_count=Count(
            "id",
            filter=Q(
                is_active=True,
                operator_evaluation_success=True,
                operator_evaluation_date__isnull=False
            )
        ),
        total_rejected_count=Count(
            "id",
            filter=Q(
                is_active=False)
            | Q(
                operator_evaluation_success=False,
                operator_evaluation_date__isnull=False
            )
        ),
    )
    return render(request, template, {'breadcrumbs': breadcrumbs,
                                      'event_counts': event_counts,
                                      'structures': organizational_structures})


@login_required
@is_structure_evaluation_operator
def events(request, structure_slug, structure=None):
    template = 'operator/events.html'
    breadcrumbs = {
                   reverse('pe_management:dashboard'): _('Home'),
                   reverse('pe_management:operator_dashboard'): _('Structure operator'),
                   '#': structure.name}
    api_url = reverse('pe_management:api_evaluation_operator_events', kwargs={'structure_slug': structure_slug})
    return render(request, template, {'breadcrumbs': breadcrumbs,
                                      'api_url': api_url,
                                      'structure_slug': structure_slug})


@login_required
@is_structure_evaluation_operator
def event(request, structure_slug, event_id, structure=None):
    event = PublicEngagementEvent.objects.filter(pk=event_id,
                                                 structure__slug=structure_slug).first()
    if not event:
        messages.add_message(request, messages.ERROR,
                             "<b>{}</b>: {}".format(_('Alert'), _('URL access is not allowed')))
        return redirect('pe_management:operator_events', structure_slug=structure_slug)

    breadcrumbs = {
                   reverse('pe_management:dashboard'): _('Home'),
                   reverse('pe_management:operator_dashboard'): _('Structure operator'),
                   reverse('pe_management:operator_events', kwargs={'structure_slug': structure_slug}): structure.name,
                   '#': event.title}
    template = 'operator/event.html'

    logs = LogEntry.objects.filter(content_type_id=ContentType.objects.get_for_model(event).pk,
                                   object_id=event.pk)

    return render(request, template, {'breadcrumbs': breadcrumbs,
                                      'event': event,
                                      'logs': logs,
                                      'structure_slug': structure_slug})


@login_required
@require_POST
@is_structure_evaluation_operator
def take_event(request, structure_slug, event_id, structure=None):
    event = get_object_or_404(PublicEngagementEvent,
                              pk=event_id,
                              structure__slug=structure_slug)

    if not event.can_be_handled_for_evaluation():
        messages.add_message(request, messages.ERROR, _("Access denied"))
        return redirect('pe_management:operator_events',
                        structure_slug=structure_slug)

    event.operator_taken_by = request.user
    event.operator_taken_date = timezone.now()
    event.modified_by = request.user
    event.save()
    messages.add_message(request, messages.SUCCESS,
                         _("Event handled successfully"))

    log_action(user=request.user,
               obj=event,
               flag=CHANGE,
               msg="[Operatore {}] Iniziativa presa in carico".format(structure_slug))

    # invia email al referente/compilatore
    subject = '{} - "{}" - {}'.format(_('Public engagement'), event.title, _('Handled'))
    body = "{} {} {}".format(request.user, _('is evaluating the event'), '.')
    send_email_to_event_referents(event, subject, body)

    return redirect('pe_management:operator_event',
                    structure_slug=structure_slug,
                    event_id=event_id)


@login_required
@is_structure_evaluation_operator
@is_editable_by_operator
def event_basic_info(request, structure_slug, event_id, structure=None, event=None):
    breadcrumbs = {
                   reverse('pe_management:dashboard'): _('Home'),
                   reverse('pe_management:operator_dashboard'): _('Structure operator'),
                   reverse('pe_management:operator_events', kwargs={'structure_slug': structure_slug}): structure.name,
                   reverse('pe_management:operator_event', kwargs={'event_id': event_id, 'structure_slug': structure_slug}): event.title,
                   '#': _('General informations')}

    template = 'event_basic_info.html'
    form = PublicEngagementEventOperatorForm(request=request, instance=event)
    # post
    if request.method == 'POST':
        form = PublicEngagementEventOperatorForm(request=request,
                                         instance=event,
                                         data=request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.modified_by = request.user
            event.save()

            log_action(user=request.user,
                       obj=event,
                       flag=CHANGE,
                       msg="[Operatore {}] Informazioni generali modificate".format(structure_slug))

            messages.add_message(request, messages.SUCCESS,
                                 _("Modified general informations successfully"))

            # invia email al referente/compilatore
            subject = '{} - "{}" - {}'.format(_('Public engagement'), event.title, _('Data modified'))
            body = '{} {} {}'.format(request.user, _('has modified the data of the event'), '.')

            send_email_to_event_referents(event, subject, body)

            return redirect("pe_management:operator_event",
                            structure_slug=structure_slug,
                            event_id=event_id)

        else:  # pragma: no cover
            messages.add_message(request, messages.ERROR,
                                 '<b>{}</b>: {}'.format(_('Alert'), _('the errors in the form below need to be fixed')))
    return render(request, template, {'breadcrumbs': breadcrumbs, 'event': event, 'form': form})


@login_required
@is_structure_evaluation_operator
@is_editable_by_operator
def event_data(request, structure_slug, event_id, structure=None, event=None):
    result = management.event_data(request=request,
                                   structure_slug=structure_slug,
                                   event_id=event_id,
                                   event=event,
                                   structure=structure)
    if result == True:
        return redirect("pe_management:operator_event",
                        structure_slug=structure_slug,
                        event_id=event_id)
    return result


@login_required
@is_structure_evaluation_operator
@is_editable_by_operator
def event_people(request, structure_slug, event_id, structure=None, event=None):
    result = management.event_people(request=request,
                                     structure_slug=structure_slug,
                                     event_id=event_id,
                                     event=event,
                                     structure=structure)
    if result == True:
        return redirect("pe_management:operator_event",
                        structure_slug=structure_slug,
                        event_id=event_id)
    return result


@login_required
@require_POST
@is_structure_evaluation_operator
@is_editable_by_operator
def event_people_delete(request, structure_slug, event_id, person_id, structure=None, event=None):
    result = management.event_people_delete(request=request,
                                            structure_slug=structure_slug,
                                            event_id=event_id,
                                            event=event,
                                            person_id=person_id)
    if result == True:
        return redirect("pe_management:operator_event",
                        structure_slug=structure_slug,
                        event_id=event_id)
    return result


@login_required
@is_structure_evaluation_operator
@is_editable_by_operator
def event_structures(request, structure_slug, event_id, structure=None, event=None):
    result = management.event_structures(request=request,
                                         structure_slug=structure_slug,
                                         event_id=event_id,
                                         event=event,
                                         structure=structure)
    if result == True:
        return redirect("pe_management:operator_event",
                        structure_slug=structure_slug,
                        event_id=event_id)
    return result


@login_required
@require_POST
@is_structure_evaluation_operator
@is_editable_by_operator
def event_structures_delete(request, structure_slug, event_id, structure_id, structure=None, event=None):
    result = management.event_structures_delete(request=request,
                                                structure_slug=structure_slug,
                                                event_id=event_id,
                                                event=event,
                                                structure_id=structure_id)
    if result == True:
        return redirect("pe_management:operator_event",
                        structure_slug=structure_slug,
                        event_id=event_id)
    return result


@login_required
@is_structure_evaluation_operator
def event_evaluation(request, structure_slug, event_id, structure=None):
    event = PublicEngagementEvent.objects.filter(pk=event_id,
                                                 structure__slug=structure_slug).first()

    if not event:
        messages.add_message(request, messages.ERROR, _("Access denied"))
        return redirect('pe_management:operator_events',
                        structure_slug=structure_slug)

    if not event.is_ready_for_evaluation():
        messages.add_message(request, messages.ERROR, _("Access denied"))
        return redirect('pe_management:operator_event',
                        structure_slug=structure_slug,
                        event_id=event_id)

    form = PublicEngagementEventEvaluationForm()
    template = 'event_evaluation.html'
    breadcrumbs = {
                   reverse('pe_management:dashboard'): _('Home'),
                   reverse('pe_management:operator_dashboard'): _('Structure operator'),
                   reverse('pe_management:operator_events', kwargs={'structure_slug': structure_slug}): structure.name,
                   reverse('pe_management:operator_event', kwargs={'event_id': event_id, 'structure_slug': structure_slug}): event.title,
                   '#': _('Evaluation')}

    if request.method == 'POST':
        form = PublicEngagementEventEvaluationForm(data=request.POST)
        if form.is_valid():
            event.operator_evaluation_date = timezone.now()
            event.operator_evaluation_success = form.cleaned_data['success']
            event.operator_evaluated_by = request.user
            event.operator_notes = form.cleaned_data['notes']
            event.modified_by = request.user
            event.save()

            log_result = "approvata" if form.cleaned_data['success'] == 'True' else "rifiutata"
            msg = "[Operatore {}] Esito valutazione: {}".format(structure_slug, log_result)
            if not form.cleaned_data['success'] == 'True':
                msg += ' {}'.format(event.operator_notes)

            log_action(user=request.user,
                       obj=event,
                       flag=CHANGE,
                       msg=msg)

            messages.add_message(request, messages.SUCCESS, _("Evaluation completed"))

            # email
            result = _('approved') if form.cleaned_data['success'] == 'True' else _('not approved')
            subject = '{} - "{}" - {}'.format(_('Public engagement'), event.title, _('Evaluation completed'))
            body = '{} {}: {}.'.format(request.user, _('has evaluated the event with the result'), result)
            if not form.cleaned_data['success'] == 'True':
                body += '\n{}: {}'.format(_('Notes'), form.cleaned_data['notes'])
            # invia email a referente/compilatore
            send_email_to_event_referents(event, subject, body)

            for involved_structure in event.data.involved_structure.all():
                send_email_to_operators(
                    involved_structure,
                    subject,
                    '{}: {}\n\n{}'.format(
                        _('Notification for operators of involved structure'),
                        involved_structure.name,
                        body
                    )
                )

            if form.cleaned_data['success'] == 'True':
                # invia email a operatori patrocinio
                if event.data.patronage_requested and not event.is_started():
                    send_email_to_patronage_operators(
                        event.structure, subject, body)
                # invia email a operatori di ateneo
                send_email_to_managers(subject, body)
                # invia email a comunicazione
                for promo_channel in event.data.promo_channel.filter(is_active=True):
                    recipients = list(promo_channel.get_contacts(structure=event.structure))
                    send_email_to_promoters(channel=promo_channel.description,
                                            title=event.title,
                                            start=event.start,
                                            end=event.end,
                                            description=event.data.description,
                                            structure=event.structure,
                                            referent=event.referent,
                                            poster=event.data.poster,
                                            recipients=recipients)

            return redirect("pe_management:operator_event",
                            structure_slug=structure_slug,
                            event_id=event_id)
        else:
            messages.add_message(request, messages.ERROR,
                                 "<b>{}</b>: {}".format(_('Alert'), _('the errors in the form below need to be fixed')))
    return render(request, template, {'breadcrumbs': breadcrumbs, 'event': event, 'form': form, 'structure_slug': structure_slug})


@login_required
@require_POST
@is_structure_evaluation_operator
def event_reopen_evaluation(request, structure_slug, event_id, structure=None):
    event = PublicEngagementEvent.objects.filter(pk=event_id,
                                                 structure__slug=structure_slug).first()
    if not event:
        messages.add_message(request, messages.ERROR, _("Access denied"))
        return redirect('pe_management:operator_events',
                        structure_slug=structure_slug)

    if not event.evaluation_can_be_reviewed():
        messages.add_message(request, messages.ERROR, _("Access denied"))
        return redirect('pe_management:operator_event',
                        structure_slug=structure_slug,
                        event_id=event_id)

    event.operator_evaluation_date = None
    event.modified_by = request.user
    event.save()

    log_action(user=request.user,
               obj=event,
               flag=CHANGE,
               msg="[Operatore {}] Valutazione riaperta".format(structure_slug))

    messages.add_message(request, messages.SUCCESS, _("Evaluation reopened"))

    # email
    subject = '{} - "{}" - {}'.format(_('Public engagement'), event.title, _('Evaluation reopened'))
    body = "{} {} {}".format(request.user, _('has reopened evaluation of the event'), '.')
    send_email_to_event_referents(event, subject, body)

    for involved_structure in event.data.involved_structure.all():
        send_email_to_operators(
            involved_structure,
            subject,
            '{}: {}\n\n{}'.format(
                _('Notification for operators of involved structure'),
                involved_structure.name,
                body
            )
        )


    if event.data.patronage_requested:
        send_email_to_patronage_operators(event.structure, subject, body)
    else:
        send_email_to_managers(subject, body)

    return redirect("pe_management:operator_event",
                    structure_slug=structure_slug,
                    event_id=event_id)
