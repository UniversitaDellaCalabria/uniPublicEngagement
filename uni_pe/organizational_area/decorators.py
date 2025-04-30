from django.utils.translation import gettext_lazy as _
from functools import wraps

from template.utils import custom_message

from . models import OrganizationalStructureOfficeEmployee


def disable_for_loaddata(signal_handler):
    """
    Decorator that turns off signal handlers when loading fixture data.
    """
    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        if kwargs.get('raw'):
            return
        signal_handler(*args, **kwargs)
    return wrapper


def belongs_to_an_office(func_to_decorate):
    """
    Check if user is manager in some OrganizationalStructure
    Employee of structure default office + staff in Django
    """
    def new_func(*original_args, **original_kwargs):
        request = original_args[0]

        if request.user.is_superuser:
            return func_to_decorate(*original_args, **original_kwargs)

        employee = OrganizationalStructureOfficeEmployee.objects.filter(employee=request.user,
                                                                        office__is_active=True,
                                                                        office__organizational_structure__is_active=True).first()
        if employee:
            return func_to_decorate(*original_args, **original_kwargs)
        return custom_message(request,
                              _("Access denied"))
    return new_func
