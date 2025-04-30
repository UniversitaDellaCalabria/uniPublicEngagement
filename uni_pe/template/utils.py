import datetime
import magic
import os

from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from organizational_area.models import (OrganizationalStructureOffice,
                                        OrganizationalStructureOfficeEmployee)


def get_datetime_delta(days):
    delta_date = timezone.now() - datetime.timedelta(days=days)
    return delta_date.replace(hour=0, minute=0, second=0)


def custom_message(request, message='', status=None):
    """
    """
    return render(request, 'custom_message.html',
                  {'avviso': message},
                  status=status)


def log_action(user, obj, flag, msg):
    LogEntry.objects.log_action(user_id=user.pk,
                                content_type_id=ContentType.objects.get_for_model(
                                    obj).pk,
                                object_id=obj.pk,
                                object_repr=obj.__str__(),
                                action_flag=flag,
                                change_message=msg)


def check_user_permission_on_model(user, model, permission='view'):
    # get Django permissions on object
    app_label = model._meta.__dict__['app_label']
    model_name = model._meta.__dict__['model_name']
    return user.has_perm(f'{app_label}.{permission}_{model_name}')


def check_user_permission_on_dashboard(user, main_model, office_slug):
    if user.is_superuser or check_user_permission_on_model(user, main_model):
        offices = OrganizationalStructureOffice.objects\
                                               .filter(slug=office_slug,
                                                       is_active=True,
                                                       organizational_structure__is_active=True)
    else:
        # get offices that I'm able to manage
        my_offices = OrganizationalStructureOfficeEmployee.objects\
                                                          .filter(employee=user,
                                                                  office__slug=office_slug,
                                                                  office__is_active=True,
                                                                  office__organizational_structure__is_active=True)\
                                                          .select_related('office')
        offices = []
        for off in my_offices:
            offices.append(off.office)
    return offices


def download_file(path, nome_file):
    """
    Downloads a file
    """
    mime = magic.Magic(mime=True)
    file_path = "{}/{}".format(path, nome_file)
    content_type = mime.from_file(file_path)

    if os.path.exists(file_path):
        with open(file_path, "rb") as fh:
            response = HttpResponse(fh.read(), content_type=content_type)
            response["Content-Disposition"] = "inline; filename=" + os.path.basename(
                file_path
            )
            return response
    return None
