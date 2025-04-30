import requests

from django.conf import settings
# from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.utils import timezone

from organizational_area.models import *
from organizational_area.utils import user_in_office

from template.settings import MSG_HEADER, MSG_FOOTER
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
    return user_in_office(user, [OPERATOR_OFFICE], structure)


def user_is_patronage_operator(user, structure=None):
    return user_in_office(user, [PATRONAGE_OFFICE], structure)


def user_is_manager(user):
    return user_in_office(user, [MANAGER_OFFICE])


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


def send_email_to_promoters(channel, title, start, end, description, poster=None, recipients=[]):
    body = """
       Canale di promozione: {channel}

       Di seguito i dettagli dell'iniziativa

       Titolo: {title}
       Inizio: {start}
       Fine: {end}
       Descrizione: {description}
    """.format(channel=channel,
               title=title,
               start=timezone.localtime(start),
               end=timezone.localtime(end),
               description=description)

    _send_email(subject=f"Promozione evento Public Engagement: {title}",
                body=body,
                attachment=poster,
                recipients=recipients)
