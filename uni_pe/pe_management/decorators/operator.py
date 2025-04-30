from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _

from organizational_area.models import *
from organizational_area.utils import user_office_structures

from .. models import *
from .. settings import *
from .. utils import *


def evaluation_operator_structures(func_to_decorate):
    """
    controlla esclusivamente la tipologia dell'utente
    e ci dice se l'utente ha accesso alla visualizzazione
    dei dati dell'evento
    """
    def new_func(*original_args, **original_kwargs):
        request = original_args[0]
        structures = user_office_structures(user=request.user,
                                            office_slug_list=[OPERATOR_OFFICE])
        if structures:
            original_kwargs['structures'] = structures
            return func_to_decorate(*original_args, **original_kwargs)
        messages.add_message(request, messages.ERROR, _('Access denied'))
        return redirect("pe_management:dashboard")
    return new_func


def is_structure_evaluation_operator(func_to_decorate):
    """
    controlla esclusivamente la tipologia dell'utente
    e ci dice se l'utente ha accesso alla visualizzazione
    dei dati dell'evento
    """
    def new_func(*original_args, **original_kwargs):
        request = original_args[0]
        structure_slug = original_kwargs['structure_slug']
        structure = get_object_or_404(OrganizationalStructure,
                                      slug=structure_slug,
                                      is_active=True)
        original_kwargs['structure'] = structure
        if user_is_operator(user=request.user, structure=structure):
            return func_to_decorate(*original_args, **original_kwargs)
        messages.add_message(request, messages.ERROR, _('Access denied'))
        return redirect("pe_management:dashboard")
    return new_func


def is_editable_by_operator(func_to_decorate):
    """
    controlla che l'attuale stato dell'evento
    renda editabile dall'utente i dati
    tutti i controlli sui permessi dell'utente vengono fatti da
    altri decoratori
    """
    def new_func(*original_args, **original_kwargs):
        request = original_args[0]
        structure_slug = original_kwargs['structure_slug']
        event_id = original_kwargs['event_id']
        event = get_object_or_404(
            PublicEngagementEvent,
            pk=event_id,
            structure__slug=structure_slug)
        if event.is_editable_by_operator():
            original_kwargs['event'] = event
            return func_to_decorate(*original_args, **original_kwargs)
        messages.add_message(request, messages.ERROR, _('Access denied'))
        return redirect("pe_management:operator_event",
                       structure_slug=structure_slug,
                       event_id=event_id)
    return new_func
