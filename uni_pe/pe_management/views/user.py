from copy import deepcopy

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.models import ADDITION, CHANGE, LogEntry
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import redirect, render, reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from organizational_area.models import *
from template.utils import *

from ..decorators.generic import *
from ..decorators.user import *
from ..forms import *
from ..models import *
from ..settings import *
from ..utils import *


@login_required
@can_manage_public_engagement
def events(request):
    template = "user/events.html"
    breadcrumbs = {reverse("pe_management:dashboard"): _("Home"), "#": _("Events")}
    api_url = reverse("pe_management:api_user_events")
    return render(request, template, {"breadcrumbs": breadcrumbs, "api_url": api_url})


@login_required
def new_event_choose_referent(request):
    request.session.pop("referent", None)
    template = "event_new.html"
    breadcrumbs = {
        reverse("pe_management:dashboard"): _("Home"),
        reverse("pe_management:user_events"): _("Events"),
        "#": _("New"),
    }

    if request.method == "POST":
        user_is_referent = request.POST["user_is_referent"]
        user_is_referent = True if user_is_referent == "true" else False

        # se è il referente ma non è un docente
        # if user_is_referent and not user_is_teacher(matricola=request.user.identificativo_dipendente):

        # se il referente non ha una matricola da dipendente
        if user_is_referent and not request.user.identificativo_dipendente:
            messages.add_message(
                request, messages.ERROR, _("You cannot enter an event as a referent")
            )
            return redirect("pe_management:user_new_event_choose_referent")

        # recupero della matricola da dipendente
        # se il referente sono io, la matricola ce l'ho già
        if user_is_referent:
            referent_id = request.user.identificativo_dipendente
        # se il referente non sono io, recupero la matricola in chiaro
        else:
            referent_id = requests.post(
                "{}/".format(API_DECRYPTED_ID),
                data={"id": request.POST["referent_id"]},
                headers={"Authorization": "Token {}".format(settings.STORAGE_TOKEN)},
            )
            if referent_id.status_code != 200:
                messages.add_message(request, messages.ERROR, _("Access denied"))
                return redirect("pe_management:user_new_event_choose_referent")

            # matricola in chiaro
            referent_id = referent_id.json()

        # recupero dati completi del referente (in entrambi i casi)
        # es: genere
        response = requests.get(
            "{}{}/".format(API_ADDRESSBOOK_FULL, referent_id.zfill(6)),
            headers={"Authorization": "Token {}".format(settings.STORAGE_TOKEN)},
        )
        if response.status_code != 200:
            messages.add_message(
                request,
                messages.ERROR,
                _("Unable to retrieve user data from our systems"),
            )
            return redirect("pe_management:user_new_event_choose_referent")

        referent_data = response.json()["results"]

        # se sono io il referente
        if user_is_referent:
            referent_user = request.user
        # creo o recupero l'utente dal db locale
        else:
            # controllo se esiste già (i dati locali potrebbero differire da quelli presenti nelle API)
            referent_user = (
                get_user_model()
                .objects.filter(taxpayer_id=referent_data["Taxpayer_ID"])
                .first()
            )
            # se l'utente è stato disattivato
            if referent_user and not referent_user.is_active:
                messages.add_message(request, messages.ERROR, _("User deactivated"))
                return redirect("pe_management:user_new_event_choose_referent")
            # se non esiste localmente lo creo
            if not referent_user:
                referent_user = get_user_model().objects.create(
                    username=referent_data["Taxpayer_ID"],
                    identificativo_dipendente=referent_data["ID"],
                    first_name=referent_data["Name"],
                    last_name=referent_data["Surname"],
                    taxpayer_id=referent_data["Taxpayer_ID"],
                    email=next(iter(referent_data["Email"]), None),
                    gender=referent_data["Gender"],
                )

        # aggiorno il dato sul genere con quello più aggiornato, sempre
        referent_user.gender = referent_data["Gender"]
        referent_user.save(update_fields=["gender"])

        # salviamo il referente corrente in sessione
        request.session["referent"] = referent_user.pk
        return redirect("pe_management:user_new_event_basic_info")

    return render(
        request, template, {"breadcrumbs": breadcrumbs, "compiled_by_user": True}
    )


@login_required
@can_manage_public_engagement
def new_event_basic_info(request):
    # se non è stato scelto il referente nella fase iniziale
    if not request.session.get("referent"):
        messages.add_message(request, messages.ERROR, _("Event referent is mandatory"))
        return redirect("pe_management:user_new_event_choose_referent")

    template = "event_basic_info.html"
    form = PublicEngagementEventForm()

    breadcrumbs = {
        reverse("pe_management:dashboard"): _("Home"),
        reverse("pe_management:user_events"): _("Events"),
        reverse("pe_management:user_new_event_choose_referent"): _("New"),
        "#": _("General informations"),
    }

    # post
    if request.method == "POST":
        form = PublicEngagementEventForm(data=request.POST)
        if form.is_valid():
            year = form.cleaned_data["start"].year
            # check sull'anno di inizio dell'evento
            if not PublicEngagementAnnualMonitoring.year_is_active(year):
                messages.add_message(
                    request,
                    messages.ERROR,
                    "<b>{}</b>: {} {} {}".format(
                        _("Alert"),
                        _("Monitoring activity year"),
                        year,
                        _("has been disabled"),
                    ),
                )
            else:
                event = form.save(commit=False)
                event.created_by = request.user
                event.modified_by = request.user
                event.referent = get_user_model().objects.get(
                    pk=request.session.get("referent")
                )
                event.save()

                log_action(
                    user=request.user,
                    obj=event,
                    flag=ADDITION,
                    msg="[Referente/Delegato] Iniziativa creata",
                )

                messages.add_message(
                    request,
                    messages.SUCCESS,
                    _(
                        "First step completed successfully. Now proceed to enter the data"
                    ),
                )
                # elimino dalla sessione il referente scelto all'inizio
                request.session.pop("referent", None)
                return redirect("pe_management:user_event", event_id=event.pk)
        else:  # pragma: no cover
            messages.add_message(
                request,
                messages.ERROR,
                "<b>{}</b>: {}".format(
                    _("Alert"), _("the errors in the form below need to be fixed")
                ),
            )
    return render(request, template, {"breadcrumbs": breadcrumbs, "form": form})


@login_required
@has_access_to_my_event
def event(request, event_id, event=None):
    template = "user/event.html"
    breadcrumbs = {
        reverse("pe_management:dashboard"): _("Home"),
        reverse("pe_management:user_events"): _("Events"),
        "#": event.title,
    }

    logs = LogEntry.objects.filter(
        content_type_id=ContentType.objects.get_for_model(event).pk, object_id=event.pk
    )

    return render(
        request, template, {"breadcrumbs": breadcrumbs, "event": event, "logs": logs}
    )


@login_required
@has_access_to_my_event
def event_basic_info(request, event_id, event=None):
    template = "event_basic_info.html"
    breadcrumbs = {
        reverse("pe_management:dashboard"): _("Home"),
        reverse("pe_management:user_events"): _("Events"),
        reverse("pe_management:user_event", kwargs={"event_id": event_id}): event.title,
        "#": _("General informations"),
    }
    form = PublicEngagementEventForm(instance=event)

    if not event.is_editable_by_user():
        messages.add_message(
            request,
            messages.ERROR,
            _(
                "It is no longer possible to change the general information of the event"
            ),
        )
        return redirect("pe_management:user_event", event_id=event.pk)

    # post
    if request.method == "POST":
        form = PublicEngagementEventForm(instance=event, data=request.POST)
        if form.is_valid():
            log_action(
                user=request.user,
                obj=event,
                flag=CHANGE,
                msg="[Referente/Delegato] Informazioni generali modificate",
            )

            event = form.save(commit=False)
            event.modified_by = request.user
            event.save()
            messages.add_message(
                request,
                messages.SUCCESS,
                _("Modified general informations successfully"),
            )
            return redirect("pe_management:user_event", event_id=event.pk)
        else:  # pragma: no cover
            messages.add_message(
                request,
                messages.ERROR,
                "<b>{}</b>: {}".format(
                    _("Alert"), _("the errors in the form below need to be fixed")
                ),
            )
    return render(
        request, template, {"breadcrumbs": breadcrumbs, "event": event, "form": form}
    )


@login_required
@has_access_to_my_event
@is_editable_by_user
def event_data(request, event_id, event=None):
    template = "event_data.html"
    instance = getattr(event, "data", None)
    form = PublicEngagementEventDataForm(instance=instance, event=event, by_user=True)

    breadcrumbs = {
        reverse("pe_management:dashboard"): _("Home"),
        reverse("pe_management:user_events"): _("Events"),
        reverse("pe_management:user_event", kwargs={"event_id": event_id}): event.title,
        "#": _("Event data"),
    }

    if request.method == "POST":
        # se l'evento è già iniziato
        # ripulisco tutti i campi riferiti a patrocinio
        # e promozione
        if event.is_started():
            event.clear_promo_info()

        form = PublicEngagementEventDataForm(
            instance=instance,
            data=request.POST,
            files=request.FILES,
            event=event,
            by_user=True,
        )
        if form.is_valid():
            log_action(
                user=request.user,
                obj=event,
                flag=CHANGE,
                msg="[Referente/Delegato] Dati iniziativa modificati"
                if instance
                else "[Referente/Delegato] Dati iniziativa inseriti",
            )

            data = form.save(commit=False)
            data.event = event
            data.modified_by = request.user
            if not instance:
                data.created_by = request.user
            data.save()
            form.save_m2m()
            event.modified_by = request.user
            event.save()

            messages.add_message(
                request, messages.SUCCESS, _("Data updated successfully")
            )
            return redirect("pe_management:user_event", event_id=event.pk)
        else:
            messages.add_message(
                request,
                messages.ERROR,
                "<b>{}</b>: {}".format(
                    _("Alert"), _("the errors in the form below need to be fixed")
                ),
            )
    return render(
        request, template, {"breadcrumbs": breadcrumbs, "event": event, "form": form}
    )


@login_required
@has_access_to_my_event
@is_editable_by_user
def event_people(request, event_id, event=None):
    data = getattr(event, "data", None)
    if not data:
        messages.add_message(
            request,
            messages.ERROR,
            "<b>{}</b>: {}".format(_("Alert"), _("event data required")),
        )
        return redirect("pe_management:user_event", event_id=event.pk)

    template = "event_people.html"
    breadcrumbs = {
        reverse("pe_management:dashboard"): _("Home"),
        reverse("pe_management:user_events"): _("Events"),
        reverse("pe_management:user_event", kwargs={"event_id": event_id}): event.title,
        "#": _("Other involved personnel"),
    }

    if request.method == "POST":
        person_id = request.POST.get("person_id")

        if not person_id:
            messages.add_message(request, messages.ERROR, _("Access denied"))
            return redirect("pe_management:user_event_people", event_id=event_id)

        decrypted_id = requests.post(
            "{}/".format(API_DECRYPTED_ID),
            data={"id": request.POST["person_id"]},
            headers={"Authorization": "Token {}".format(settings.STORAGE_TOKEN)},
        )
        response = requests.get(
            "{}{}/".format(API_ADDRESSBOOK_FULL, decrypted_id.json()),
            headers={"Authorization": "Token {}".format(settings.STORAGE_TOKEN)},
        )
        if response.status_code != 200:
            messages.add_message(request, messages.ERROR, _("Access denied"))
            return redirect("pe_management:user_event_people", event_id=event_id)
        person_data = response.json()["results"]
        person = (
            get_user_model()
            .objects.filter(taxpayer_id=person_data["Taxpayer_ID"])
            .first()
        )
        # aggiorno il dato sul genere (potrebbe non essere presente localmente)
        if person and not person.gender:
            person.gender = person_data["Gender"]
            person.save(update_fields=["gender"])
        # se non esiste localmente lo creo
        if not person:
            person = get_user_model().objects.create(
                username=person_data["Taxpayer_ID"],
                identificativo_dipendente=person_data["ID"],
                first_name=person_data["Name"],
                last_name=person_data["Surname"],
                taxpayer_id=person_data["Taxpayer_ID"],
                email=next(iter(person_data["Email"]), None),
                gender=person_data["Gender"],
            )
        if person == event.referent:
            messages.add_message(
                request,
                messages.ERROR,
                "{} {}".format(person, _("is the event referent")),
            )
        elif data.involved_personnel.filter(pk=person.pk).exists():
            messages.add_message(
                request, messages.ERROR, "{} {}".format(person, _("already exists"))
            )
        else:
            data.involved_personnel.add(person)
            data.modified_by = request.user
            data.save()
            event.modified_by = request.user
            event.save()

            log_action(
                user=request.user,
                obj=event,
                flag=CHANGE,
                msg="[Referente/Delegato] Altro personale coinvolto: aggiunto {}".format(
                    person
                ),
            )

            messages.add_message(
                request,
                messages.SUCCESS,
                "{} {}".format(person, _("added successfully")),
            )
        return redirect("pe_management:user_event", event_id=event.pk)
    return render(request, template, {"breadcrumbs": breadcrumbs, "event": event})


@login_required
@require_POST
@has_access_to_my_event
@is_editable_by_user
def event_people_delete(request, event_id, person_id, event=None):
    if not person_id:
        messages.add_message(request, messages.ERROR, _("Access denied"))
        return redirect("pe_management:user_event", event_id=event.pk)
    person = event.data.involved_personnel.filter(pk=person_id).first()
    if not person:
        messages.add_message(request, messages.ERROR, _("Personnel does not exist"))
    else:
        event.data.involved_personnel.remove(person)
        event.data.modified_by = request.user
        event.data.save()
        event.modified_by = request.user
        event.save()

        log_action(
            user=request.user,
            obj=event,
            flag=CHANGE,
            msg="[Referente/Delegato] Altro personale coinvolto: rimosso {}".format(
                person
            ),
        )

        messages.add_message(
            request, messages.SUCCESS, _("Personnel successfully removed")
        )
    return redirect("pe_management:user_event", event_id=event.pk)


@login_required
@has_access_to_my_event
@is_editable_by_user
def event_structures(request, event_id, event=None):
    data = getattr(event, "data", None)
    if not data:
        messages.add_message(
            request,
            messages.ERROR,
            "<b>{}</b>: {}".format(_("Alert"), _("event data required")),
        )
        return redirect("pe_management:user_event", event_id=event.pk)

    template = "event_structures.html"
    breadcrumbs = {
        reverse("pe_management:dashboard"): _("Home"),
        reverse("pe_management:user_events"): _("Events"),
        reverse("pe_management:user_event", kwargs={"event_id": event_id}): event.title,
        "#": _("Other involved structures"),
    }

    form = PublicEngagementStructureForm()

    if request.method == "POST":
        form = PublicEngagementStructureForm(request.POST)

        if form.is_valid():
            structure_id = form.cleaned_data["structure"]

            if not structure_id:
                messages.add_message(request, messages.ERROR, _("Access denied"))
                return redirect(
                    "pe_management:user_event_structures", event_id=event_id
                )

            structure = OrganizationalStructure.objects.filter(
                pk=structure_id, is_active=True
            ).first()
            if structure == event.structure:
                messages.add_message(
                    request,
                    messages.ERROR,
                    "{} {}".format(structure, _("is the event structure")),
                )
            elif data.involved_structure.filter(pk=structure.pk).exists():
                messages.add_message(
                    request,
                    messages.ERROR,
                    "{} {}".format(structure, _("already exists")),
                )
            else:
                data.involved_structure.add(structure)
                data.modified_by = request.user
                data.save()
                event.modified_by = request.user
                event.save()

                log_action(
                    user=request.user,
                    obj=event,
                    flag=CHANGE,
                    msg="[Referente/Delegato] Altra struttura coinvolta: aggiunto {}".format(
                        structure
                    ),
                )

                messages.add_message(
                    request,
                    messages.SUCCESS,
                    "{} {}".format(structure, _("added successfully")),
                )
            return redirect("pe_management:user_event", event_id=event.pk)
        else:
            messages.add_message(
                request,
                messages.ERROR,
                "<b>{}</b>: {}".format(
                    _("Alert"), _("the errors in the form below need to be fixed")
                ),
            )
    return render(
        request, template, {"breadcrumbs": breadcrumbs, "event": event, "form": form}
    )


@login_required
@require_POST
@has_access_to_my_event
@is_editable_by_user
def event_structures_delete(request, event_id, structure_id, event=None):
    if not structure_id:
        messages.add_message(request, messages.ERROR, _("Access denied"))
        return redirect("pe_management:user_event", event_id=event.pk)
    structure = event.data.involved_structure.filter(pk=structure_id).first()
    if not structure:
        messages.add_message(request, messages.ERROR, _("Structure does not exist"))
    else:
        event.data.involved_structure.remove(structure)
        event.data.modified_by = request.user
        event.data.save()
        event.modified_by = request.user
        event.save()

        log_action(
            user=request.user,
            obj=event,
            flag=CHANGE,
            msg="[Referente/Delegato] Altra struttura coinvolta: rimosso {}".format(
                structure
            ),
        )

        messages.add_message(
            request, messages.SUCCESS, _("Structure successfully removed")
        )
    return redirect("pe_management:user_event", event_id=event.pk)


@login_required
@has_access_to_my_event
@has_report_editable
def event_report(request, event_id, event=None):
    if getattr(event, "report", None) and event.report.edited_by_manager:
        messages.add_message(request, messages.ERROR, _("Access denied"))
        return redirect("pe_management:user_event", event_id=event_id)

    template = "user/event_report.html"
    instance = PublicEngagementEventReport.objects.filter(event=event).first()
    form = PublicEngagementEventReportForm(instance=instance)

    breadcrumbs = {
        reverse("pe_management:dashboard"): _("Home"),
        reverse("pe_management:user_events"): _("Events"),
        reverse("pe_management:user_event", kwargs={"event_id": event_id}): event.title,
        "#": _("Monitoring data"),
    }

    if request.method == "POST":
        form = PublicEngagementEventReportForm(instance=instance, data=request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.event = event
            report.modified_by = request.user
            if not instance:
                report.created_by = request.user
            report.save()
            form.save_m2m()
            event.modified_by = request.user
            event.save()

            log_action(
                user=request.user,
                obj=event,
                flag=CHANGE,
                msg="[Referente/Delegato] Dati di monitoraggio caricati"
                if instance
                else "[Referente/Delegato] Dati di monitoraggio modificati",
            )

            messages.add_message(
                request, messages.SUCCESS, _("Monitoring data modified successfully")
            )
            return redirect("pe_management:user_event", event_id=event.pk)
        else:
            messages.add_message(
                request,
                messages.ERROR,
                "<b>{}</b>: {}".format(
                    _("Alert"), _("the errors in the form below need to be fixed")
                ),
            )
    return render(
        request, template, {"breadcrumbs": breadcrumbs, "event": event, "form": form}
    )


@login_required
@require_POST
@has_access_to_my_event
def event_request_evaluation(request, event_id, event=None):
    if event.is_ready_for_request_evaluation():
        # se l'evento è già iniziato
        # ripulisco tutti i campi riferiti a patrocinio
        # e promozione
        if event.is_started():
            event.clear_promo_info()

        event.to_evaluate = True
        event.evaluation_request_date = timezone.now()
        event.evaluation_request_by = request.user
        event.modified_by = request.user
        event.save()

        log_action(
            user=request.user,
            obj=event,
            flag=CHANGE,
            msg="[Referente/Delegato] Richiesta di validazione inviata",
        )

        messages.add_message(request, messages.SUCCESS, _("Evaluation request sent"))

        subject = '{} - "{}" - {}'.format(
            _("Public engagement"), event.title, _("Evaluation request sent")
        )
        body = "{} {}. {}: {}".format(
            request.user,
            _("requested the evaluation of the event"),
            _("Click here"),
            request.build_absolute_uri(
                reverse(
                    "pe_management:operator_event",
                    kwargs={
                        "structure_slug": event.structure.slug,
                        "event_id": event.pk,
                    },
                )
            ),
        )
        send_email_to_operators(structure=event.structure, subject=subject, body=body)
    else:
        messages.add_message(
            request,
            messages.ERROR,
            "<b>{}</b>: {}".format(
                _("Alert"), _("evaluation conditions are not satisfied")
            ),
        )
    return redirect("pe_management:user_event", event_id=event.pk)


@login_required
@require_POST
@has_access_to_my_event
def event_request_evaluation_cancel(request, event_id, event=None):
    if not event.evaluation_request_can_be_reviewed():
        messages.add_message(request, messages.ERROR, _("Access denied"))
        return redirect("pe_management:user_event", event_id=event_id)

    event.to_evaluate = False
    event.modified_by = request.user
    event.save()

    log_action(
        user=request.user,
        obj=event,
        flag=CHANGE,
        msg="[Referente/Delegato] Richiesta di validazione annullata",
    )

    messages.add_message(request, messages.SUCCESS, _("Evaluation request cancelled"))

    subject = '{} - "{}" - {}'.format(
        _("Public engagement"), event.title, _("Evaluation request cancelled")
    )
    body = "{} {}".format(request.user, _("has cancelled the evaluation request"))
    send_email_to_operators(structure=event.structure, subject=subject, body=body)

    return redirect("pe_management:user_event", event_id=event.pk)


@login_required
@has_access_to_my_event
def event_clone(request, event_id, event=None):
    new_event = PublicEngagementEvent.objects.create(
        title=event.title,
        start=event.start,
        end=event.end,
        referent=event.referent,
        structure=event.structure,
        created_by=request.user,
        modified_by=request.user,
        created=timezone.now(),
        modified=timezone.now(),
    )
    new_data = deepcopy(event.data)
    new_data.pk = None
    new_data.event = new_event
    new_data.created = timezone.now()
    new_data.modified = timezone.now()
    new_data.created_by = request.user
    new_data.modified_by = request.user
    new_data.save()

    new_data.involved_personnel.set(event.data.involved_personnel.all())
    new_data.recipient.set(event.data.recipient.all())
    new_data.target.set(event.data.target.all())
    new_data.promo_channel.set(event.data.promo_channel.all())
    new_data.promo_tool.set(event.data.promo_tool.all())

    messages.add_message(
        request,
        messages.SUCCESS,
        "{} <b>{}</b> {}".format(_("Event"), event.title, _("duplicated")),
    )
    return redirect("pe_management:user_event", event_id=new_event.pk)


@login_required
@require_POST
@has_access_to_my_event
def event_delete(request, event_id, event=None):
    if event.to_evaluate or event.created_by_manager:
        messages.add_message(request, messages.ERROR, _("Access denied"))
        return redirect("pe_management:user_event", event_id=event_id)

    messages.add_message(
        request,
        messages.SUCCESS,
        "{} <b>{}</b> {}".format(_("Event"), event.title, _("removed")),
    )
    event.delete()
    return redirect("pe_management:user_events")
