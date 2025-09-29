import csv
import requests

from django.conf import settings
# from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.utils import timezone

from organizational_area.models import *
from organizational_area.utils import user_in_office

from template.settings import MSG_HEADER, MSG_FOOTER
from . models import *
from . settings import *


# def user_is_teacher(matricola='', encrypted=False):
    # if not matricola:
        # return False
    # if not encrypted:
        # response = requests.post(f'{API_ENCRYPTED_ID}',
                                 # data={'id': matricola},
                                 # headers={'Authorization': f'Token {settings.STORAGE_TOKEN}'})
        # if response.status_code == 200:
            # matricola = response.json()
        # else:
            # return False
    # response = requests.get(f"{API_TEACHER_URL}{matricola}")
    # if response.status_code == 200:
        # return True
    # return False


def user_is_operator(user, structure=None):
    return user_in_office(user=user,
                          office_slug_list=[OPERATOR_OFFICE],
                          structure=structure)


def user_is_patronage_operator(user, structure=None):
    return user_in_office(user=user,
                          office_slug_list=[PATRONAGE_OFFICE],
                          structure=structure)


def user_is_manager(user):
    return user_in_office(user=user,
                          office_slug_list=[MANAGER_OFFICE])


def _send_email(subject, body, attachment=None, recipients=[]):
    email = EmailMessage(
        subject=subject,
        body=MSG_HEADER + body + MSG_FOOTER,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipients,
    )
    if attachment: email.attach_file(attachment.path)
    email.send(fail_silently=True)


def send_email_to_event_referents(event, subject, body):
    recipients = [event.referent.email]
    if event.created_by.email not in recipients:
        recipients.append(event.created_by.email)
    _send_email(subject=subject, body=body, recipients=recipients)


def send_email_to_operators(structure, subject, body):
    recipients = OrganizationalStructureOfficeEmployee.objects.filter(employee__is_active=True,
                                                                      office__is_active=True,
                                                                      office__slug=OPERATOR_OFFICE,
                                                                      office__organizational_structure=structure,
                                                                      office__organizational_structure__is_active=True).values_list('employee__email', flat=True)
    _send_email(subject=subject, body=body, recipients=recipients)


def send_email_to_patronage_operators(structure, subject, body):
    recipients = OrganizationalStructureOfficeEmployee.objects.filter(employee__is_active=True,
                                                                      office__is_active=True,
                                                                      office__slug=PATRONAGE_OFFICE,
                                                                      office__organizational_structure=structure,
                                                                      office__organizational_structure__is_active=True).values_list('employee__email', flat=True)
    _send_email(subject=subject, body=body, recipients=recipients)


def send_email_to_managers(subject, body, to_alias=True):
    recipients = MANAGER_ALIAS_EMAILS
    if not to_alias:
        recipients = OrganizationalStructureOfficeEmployee.objects.filter(employee__is_active=True,
                                                                          office__is_active=True,
                                                                          office__slug=MANAGER_OFFICE,
                                                                          office__organizational_structure__is_active=True).values_list('employee__email', flat=True)
    _send_email(subject=subject, body=body, recipients=recipients)


def send_email_to_promoters(channel, title, start, end, description, structure, referent, poster=None, recipients=[]):
    body = """
       Canale di promozione: {channel}

       Di seguito i dettagli dell'iniziativa

       Titolo: {title}
       Inizio: {start}
       Fine: {end}
       Struttura: {structure}
       Referente scientifico: {referent}
       Descrizione: {description}
    """.format(channel=channel,
               title=title,
               start=timezone.localtime(start),
               end=timezone.localtime(end),
               description=description,
               structure=structure,
               referent=referent)

    _send_email(subject=f"Promozione evento Public Engagement: {channel}",
                body=body,
                attachment=poster,
                recipients=recipients)


def export_csv(events, file_name):
    response = HttpResponse(
        content_type="text/csv",
        headers={'Content-Disposition': f'attachment; filename="{file_name}.csv"'},
    )

    writer = csv.writer(response)

    # header
    header = [
        PublicEngagementEvent._meta.get_field("id").verbose_name,
        PublicEngagementEvent._meta.get_field("created").verbose_name,
        PublicEngagementEvent._meta.get_field("modified").verbose_name,
        PublicEngagementEvent._meta.get_field("start").verbose_name,
        PublicEngagementEvent._meta.get_field("end").verbose_name,
        PublicEngagementEvent._meta.get_field("title").verbose_name,
        PublicEngagementEvent._meta.get_field("referent").verbose_name,
        PublicEngagementEvent._meta.get_field("structure").verbose_name,
        PublicEngagementEvent._meta.get_field("evaluation_request_date").verbose_name,
        PublicEngagementEvent._meta.get_field("evaluation_request_by").verbose_name,
        PublicEngagementEvent._meta.get_field("operator_taken_date").verbose_name,
        PublicEngagementEvent._meta.get_field("operator_taken_by").verbose_name,
        PublicEngagementEvent._meta.get_field("operator_evaluation_date").verbose_name,
        PublicEngagementEvent._meta.get_field("operator_evaluation_success").verbose_name,
        PublicEngagementEvent._meta.get_field("operator_evaluated_by").verbose_name,
        PublicEngagementEvent._meta.get_field("operator_notes").verbose_name,
        PublicEngagementEvent._meta.get_field("patronage_operator_taken_date").verbose_name,
        PublicEngagementEvent._meta.get_field("patronage_operator_taken_by").verbose_name,
        PublicEngagementEvent._meta.get_field("patronage_granted").verbose_name,
        PublicEngagementEvent._meta.get_field("patronage_granted_date").verbose_name,
        PublicEngagementEvent._meta.get_field("patronage_granted_by").verbose_name,
        PublicEngagementEvent._meta.get_field("patronage_granted_notes").verbose_name,
        PublicEngagementEvent._meta.get_field("created_by_manager").verbose_name,
        PublicEngagementEvent._meta.get_field("edited_by_manager").verbose_name,
        PublicEngagementEvent._meta.get_field("is_active").verbose_name,
        PublicEngagementEvent._meta.get_field("disabled_notes").verbose_name,
        # data
        PublicEngagementEventData._meta.get_field("event_type").verbose_name,
        PublicEngagementEventData._meta.get_field("description").verbose_name,
        PublicEngagementEventData._meta.get_field("involved_personnel").verbose_name,
        PublicEngagementEventData._meta.get_field("involved_structure").verbose_name,
        PublicEngagementEventData._meta.get_field("project_name").verbose_name,
        PublicEngagementEventData._meta.get_field("recipient").verbose_name,
        PublicEngagementEventData._meta.get_field("other_recipients").verbose_name,
        PublicEngagementEventData._meta.get_field("target").verbose_name,
        PublicEngagementEventData._meta.get_field("method_of_execution").verbose_name,
        PublicEngagementEventData._meta.get_field("geographical_dimension").verbose_name,
        PublicEngagementEventData._meta.get_field("organizing_subject").verbose_name,
        PublicEngagementEventData._meta.get_field("promo_channel").verbose_name,
        PublicEngagementEventData._meta.get_field("patronage_requested").verbose_name,
        PublicEngagementEventData._meta.get_field("promo_tool").verbose_name,
        # report
        PublicEngagementEventReport._meta.get_field("participants").verbose_name,
        PublicEngagementEventReport._meta.get_field("budget").verbose_name,
        PublicEngagementEventReport._meta.get_field("monitoring_activity").verbose_name,
        PublicEngagementEventReport._meta.get_field("impact_evaluation").verbose_name,
        PublicEngagementEventReport._meta.get_field("scientific_area").verbose_name,
        PublicEngagementEventReport._meta.get_field("collaborator_type").verbose_name,
        PublicEngagementEventReport._meta.get_field("website").verbose_name,
        PublicEngagementEventReport._meta.get_field("notes").verbose_name,
        PublicEngagementEventReport._meta.get_field("edited_by_manager").verbose_name,
    ]

    writer.writerow(header)

    for event in events:
        data = [
            event.pk,
            timezone.localtime(event.created),
            timezone.localtime(event.modified),
            timezone.localtime(event.start),
            timezone.localtime(event.end),
            event.title,
            event.referent,
            event.structure,
            timezone.localtime(event.evaluation_request_date) if event.evaluation_request_date else "",
            event.evaluation_request_by,
            timezone.localtime(event.operator_taken_date) if event.operator_taken_date else "",
            event.operator_taken_by,
            timezone.localtime(event.operator_evaluation_date) if event.operator_evaluation_date else "",
            event.operator_evaluation_success,
            event.operator_evaluated_by,
            event.operator_notes,
            timezone.localtime(event.patronage_operator_taken_date) if event.patronage_operator_taken_date else "",
            event.patronage_operator_taken_by,
            event.patronage_granted,
            timezone.localtime(event.patronage_granted_date) if event.patronage_granted_date else "",
            event.patronage_granted_by,
            event.patronage_granted_notes,
            event.created_by_manager,
            event.edited_by_manager,
            event.is_active,
            event.disabled_notes,
        ]

        if hasattr(event, 'data'):
            data.extend([
                event.data.event_type,
                event.data.description,
                ", ".join(str(p) for p in event.data.involved_personnel.all()),
                ", ".join(str(s) for s in event.data.involved_structure.all()),
                event.data.project_name,
                ", ".join(event.data.recipient.values_list("description", flat=True)),
                event.data.other_recipients,
                ", ".join(event.data.target.values_list("description", flat=True)),
                event.data.method_of_execution.description,
                event.data.geographical_dimension,
                event.data.organizing_subject,
                ", ".join(event.data.promo_channel.values_list("description", flat=True)),
                event.data.patronage_requested,
                ", ".join(event.data.promo_tool.values_list("description", flat=True)),
            ])

        if hasattr(event, 'report'):
            data.extend([
                event.report.participants,
                event.report.budget,
                event.report.monitoring_activity,
                event.report.impact_evaluation,
                ", ".join(event.report.scientific_area.values_list("description", flat=True)),
                ", ".join(event.report.collaborator_type.values_list("description", flat=True)),
                event.report.website,
                event.report.notes,
                event.report.edited_by_manager,
            ])

        writer.writerow(data)
    return response
