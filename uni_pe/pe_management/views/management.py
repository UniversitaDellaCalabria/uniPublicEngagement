import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.models import CHANGE
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from organizational_area.models import OrganizationalStructure
from template.utils import *

from ..forms import *
from ..models import *
from ..settings import *
from ..utils import *


def event_data(
    request,
    structure_slug,
    breadcrumbs,
    event,
    by_manager=False,
):
    template = "event_data.html"
    form = PublicEngagementEventDataForm(
        instance=getattr(event, "data", None), event=event
    )
    if request.method == "POST":
        form = PublicEngagementEventDataForm(
            instance=getattr(event, "data", None),
            data=request.POST,
            files=request.FILES,
            event=event,
        )
        if form.is_valid():
            data = form.save(commit=False)
            data.event = event
            data.modified_by = request.user
            data.created_by = request.user
            data.save()
            form.save_m2m()
            event.modified_by = request.user

            if by_manager:
                event.edited_by_manager = True
            else:
                event.edited_by_operator = True
            event.save()

            if by_manager:
                msg = "[Operatore di Ateneo] Dati iniziativa modificati"
            else:
                msg = "[Operatore di Struttura] Dati iniziativa modificati"

            log_action(user=request.user, obj=event, flag=CHANGE, msg=msg)

            messages.add_message(
                request, messages.SUCCESS, _("Data updated successfully")
            )

            # invia email al referente/compilatore
            subject = '{} - "{}" - {}'.format(
                _("Public engagement"), event.title, _("Data modified")
            )
            body = "{} {} {}".format(
                request.user, _("has modified the data of the event"), "."
            )

            send_email_to_event_referents(event, subject, body)

            # invia email agli operatori dipartimentali
            if by_manager:
                send_email_to_operators(event.structure, subject, body)

            return True
        else:
            for error in form.errors.get_json_data():
                for message in form.errors.get_json_data()[error]:
                    messages.add_message(
                        request,
                        messages.ERROR,
                        "<b>{}</b>: {}".format(form.fields[error].label, message["message"]),
                    )
    return render(
        request,
        template,
        {
            "breadcrumbs": breadcrumbs,
            "event": event,
            "form": form,
            "structure_slug": structure_slug,
        },
    )


def event_people(
    request,
    structure_slug,
    breadcrumbs,
    event,
    by_manager=False,
):
    data = event.data
    template = "event_people.html"

    if request.method == "POST":
        # recupero dati completi del referente (in entrambi i casi)
        # es: genere
        person_id = request.POST.get("person_id")
        if not person_id:
            raise PermissionDenied()
        decrypted_id = requests.post(
            "{}{}".format(API_DECRYPTED_ID, "/"),
            data={"id": request.POST["person_id"]},
            headers={"Authorization": "Token {}".format(settings.STORAGE_TOKEN)},
        )
        response = requests.get(
            "{}{}".format(API_ADDRESSBOOK_FULL, decrypted_id.json()),
            headers={"Authorization": "Token {}".format(settings.STORAGE_TOKEN)},
        )
        if response.status_code != 200:
            raise PermissionDenied()
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

            if by_manager:
                event.edited_by_manager = True
            else:
                event.edited_by_operator = True
            event.save()

            if by_manager:
                msg = "[Operatore di Ateneo] Altro personale coinvolto: aggiunto {}".format(
                    person
                )
            else:
                msg = "[Operatore di Struttura] Altro personale coinvolto: aggiunto {}".format(
                    person
                )

            log_action(user=request.user, obj=event, flag=CHANGE, msg=msg)

            messages.add_message(
                request,
                messages.SUCCESS,
                "{} {}".format(person, _("added successfully")),
            )

            # invia email al referente/compilatore
            subject = '{} - "{}" - {}'.format(
                _("Public engagement"), event.title, _("Data modified")
            )
            body = "{} {} {}".format(
                request.user, _("has modified the data of the event"), "."
            )
            send_email_to_event_referents(event, subject, body)

            # invia email agli operatori dipartimentali
            if by_manager:
                send_email_to_operators(event.structure, subject, body)

        return True
    return render(
        request,
        template,
        {"breadcrumbs": breadcrumbs, "event": event, "structure_slug": structure_slug},
    )


def event_people_delete(request, structure_slug, person_id, event, by_manager=False):
    if not person_id:
        raise PermissionDenied()
    person = event.data.involved_personnel.filter(pk=person_id).first()
    if not person:
        messages.add_message(request, messages.ERROR, _("Personnel does not exist"))
    else:
        event.data.involved_personnel.remove(person)
        event.data.modified_by = request.user
        event.data.save()
        event.modified_by = request.user

        if by_manager:
            event.edited_by_manager = True
        else:
            event.edited_by_operator = True
        event.save()

        if by_manager:
            msg = "[Operatore di Ateneo] Altro personale coinvolto: rimosso {}".format(
                person
            )
        else:
            msg = (
                "[Operatore di Struttura] Altro personale coinvolto: rimosso {}".format(
                    person
                )
            )

        log_action(user=request.user, obj=event, flag=CHANGE, msg=msg)

        messages.add_message(
            request, messages.SUCCESS, _("Personnel removed successfully")
        )

        # invia email al referente/compilatore
        subject = '{} - "{}" - {}'.format(
            _("Public engagement"), event.title, _("Data modified")
        )
        body = "{} {} {}".format(
            request.user, _("has modified the data of the event"), "."
        )
        send_email_to_event_referents(event, subject, body)

        # invia email agli operatori dipartimentali
        if by_manager:
            send_email_to_operators(event.structure, subject, body)

    return redirect(
        "pe_management:manager_event", structure_slug=structure_slug, event_id=event.pk
    )


def event_structures(
    request,
    structure_slug,
    breadcrumbs,
    event,
    by_manager=False,
):
    data = event.data
    template = "event_structures.html"
    form_internal = PublicEngagementStructureForm()
    form_external = PublicEngagementDataInvolvedExternalStructuresForm(instance=data)

    if request.method == "POST":
        form_internal = PublicEngagementStructureForm(request.POST)
        form_external = PublicEngagementDataInvolvedExternalStructuresForm(
            instance=data, data=request.POST
        )
        if form_internal.is_valid():
            structure_id = form_internal.cleaned_data["structure"]
            new_structure = OrganizationalStructure.objects.filter(
                pk=structure_id, is_active=True
            ).first()

            if new_structure == event.structure:
                messages.add_message(
                    request,
                    messages.ERROR,
                    "{} {}".format(new_structure, _("is the event structure")),
                )
            elif data.involved_structure.filter(pk=new_structure.pk).exists():
                messages.add_message(
                    request,
                    messages.ERROR,
                    "{} {}".format(new_structure, _("already exists")),
                )
            else:
                data.involved_structure.add(new_structure)
                data.modified_by = request.user
                data.save()
                event.modified_by = request.user

                if by_manager:
                    event.edited_by_manager = True
                else:
                    event.edited_by_operator = True
                event.save()

                if by_manager:
                    msg = "[Operatore di Ateneo] Altra struttura coinvolta: aggiunto {}".format(
                        new_structure
                    )
                else:
                    msg = "[Operatore di Struttura] Altra struttura coinvolta: aggiunto {}".format(
                        new_structure
                    )

                log_action(user=request.user, obj=event, flag=CHANGE, msg=msg)

                messages.add_message(
                    request,
                    messages.SUCCESS,
                    "{} {}".format(new_structure, _("added successfully")),
                )

                # invia email al referente/compilatore
                subject = '{} - "{}" - {}'.format(
                    _("Public engagement"), event.title, _("Data modified")
                )
                body = "{} {} {}".format(
                    request.user, _("has modified the data of the event"), "."
                )
                send_email_to_event_referents(event, subject, body)

                # invia email agli operatori dipartimentali
                if by_manager:
                    send_email_to_operators(event.structure, subject, body)

            return True
        elif form_external.is_valid():
            data.involved_external_structures = form_external.cleaned_data[
                "involved_external_structures"
            ]
            data.modified_by = request.user
            data.save()
            event.modified_by = request.user
            event.save()

            if by_manager:
                msg = "[Operatore di Ateneo] Strutture esterne coinvolte modificate: {}".format(
                    form_external.cleaned_data["involved_external_structures"]
                )
            else:
                msg = "[Operatore di Struttura] Strutture esterne coinvolte modificate: {}".format(
                    form_external.cleaned_data["involved_external_structures"]
                )

            log_action(user=request.user, obj=event, flag=CHANGE, msg=msg)

            messages.add_message(
                request,
                messages.SUCCESS,
                _("Involved external structures added successfully"),
            )

            return True
        else:
            messages.add_message(
                request,
                messages.ERROR,
                "<b>{}</b>: {}".format(
                    _("Alert"), _("the errors in the form below need to be fixed")
                ),
            )
    return render(
        request,
        template,
        {
            "breadcrumbs": breadcrumbs,
            "event": event,
            "form_internal": form_internal,
            "form_external": form_external,
            "structure_slug": structure_slug,
        },
    )


def event_structures_delete(
    request, structure_slug, structure_id, event, by_manager=False
):
    if not structure_id:
        raise PermissionDenied()
    structure = event.data.involved_structure.filter(pk=structure_id).first()
    if not structure:
        messages.add_message(request, messages.ERROR, _("Structure does not exist"))
    else:
        event.data.involved_structure.remove(structure)
        event.data.modified_by = request.user
        event.data.save()
        event.modified_by = request.user

        if by_manager:
            event.edited_by_manager = True
        else:
            event.edited_by_operator = True
        event.save()

        if by_manager:
            msg = "[Operatore di Ateneo] Altra struttura coinvolta: rimosso {}".format(
                structure
            )
        else:
            msg = (
                "[Operatore di Struttura] Altra struttura coinvolta: rimosso {}".format(
                    structure
                )
            )

        log_action(user=request.user, obj=event, flag=CHANGE, msg=msg)

        messages.add_message(
            request, messages.SUCCESS, _("Structure removed successfully")
        )

        # invia email al referente/compilatore
        subject = '{} - "{}" - {}'.format(
            _("Public engagement"), event.title, _("Data modified")
        )
        body = "{} {} {}".format(
            request.user, _("has modified the data of the event"), "."
        )
        send_email_to_event_referents(event, subject, body)

        # invia email agli operatori dipartimentali
        if by_manager:
            send_email_to_operators(event.structure, subject, body)

    return redirect(
        "pe_management:manager_event", structure_slug=structure_slug, event_id=event.pk
    )
