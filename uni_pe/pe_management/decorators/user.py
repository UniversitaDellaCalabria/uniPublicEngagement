from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _

from organizational_area.models import *

from .. models import *
from .. settings import *
from .. utils import *


def has_access_to_my_event(func_to_decorate):
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

        # se l'evento è stato creato da me (in qualità di delegato)
        if event.created_by == request.user:
            return func_to_decorate(*original_args, **original_kwargs)

        # anche se l'evento è stato creato da me devo comunque
        # dimostrare di avere un legame con la struttura di riferimento
        # dell'evento, o essere un utente manager

        # se sono un operatore della struttura a cui è collegato l'evento
        # if user_is_operator(user=request.user, structure=event.structure):
            # return func_to_decorate(*original_args, **original_kwargs)

        messages.add_message(request, messages.ERROR, _('Access denied'))
        return redirect("pe_management:user_events")
    return new_func


def is_editable_by_user(func_to_decorate):
    """
    controlla che l'attuale stato dell'evento
    renda editabile dall'utente i dati
    tutti i controlli sui permessi dell'utente vengono fatti da
    altri decoratori
    """
    def new_func(*original_args, **original_kwargs):
        request = original_args[0]
        event = original_kwargs['event']
        if event.is_editable_by_user():
            return func_to_decorate(*original_args, **original_kwargs)
        messages.add_message(request, messages.ERROR, _('Access denied'))
        return redirect("pe_management:user_event", event_id=event.pk)
    return new_func


def has_report_editable(func_to_decorate):
    """
    controlla che l'attuale stato dell'evento
    renda editabile dall'utente il report
    tutti i controlli sui permessi dell'utente vengono fatti da
    altri decoratori
    """
    def new_func(*original_args, **original_kwargs):
        request = original_args[0]
        event = original_kwargs.get('event') or get_object_or_404(PublicEngagementEvent, pk=original_kwargs['event_id'])
        if event.has_report_editable():
            return func_to_decorate(*original_args, **original_kwargs)
        messages.add_message(request, messages.ERROR, _('Access denied'))
        return redirect("pe_management:user_event",
                        event_id=original_kwargs['event_id'])
    return new_func
