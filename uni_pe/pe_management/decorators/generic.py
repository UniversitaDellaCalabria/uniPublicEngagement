from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _

from organizational_area.models import *
from organizational_area.utils import user_in_office

from .. models import *
from .. settings import *
from .. utils import *


def can_manage_public_engagement(func_to_decorate):
    """
    """
    def new_func(*original_args, **original_kwargs):
        request = original_args[0]
        if request.user.identificativo_dipendente:
            return func_to_decorate(*original_args, **original_kwargs)
        messages.add_message(request, messages.ERROR, _('Access denied'))
        return redirect("template:dashboard")
    return new_func


def has_access_to_event(func_to_decorate):
    """
    controlla esclusivamente la tipologia dell'utente
    e ci dice se l'utente ha accesso alla visualizzazione
    dei dati dell'evento
    """
    def new_func(*original_args, **original_kwargs):
        request = original_args[0]
        event_id = original_kwargs['event_id']
        event = get_object_or_404(PublicEngagementEvent, pk=event_id)
        original_kwargs['event'] = event

        # se sono il referente dell'evento
        if event.referent == request.user:
            return func_to_decorate(*original_args, **original_kwargs)

        # se sono un operatore della struttura a cui è collegato l'evento
        if user_is_operator(user=request.user, structure=event.structure):
            return func_to_decorate(*original_args, **original_kwargs)

        # se sono un manager
        if user_is_manager(request.user):
            return func_to_decorate(*original_args, **original_kwargs)

        messages.add_message(request, messages.ERROR, _('Access denied'))
        return redirect("pe_management:dashboard")
    return new_func
