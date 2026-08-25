from pe_management.settings import STRUCTURE_PATRONAGE_OP_OFFICE
from pe_management.settings import STRUCTURE_OP_OFFICE
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext_lazy as _
from organizational_area.models import *
from organizational_area.utils import user_in_office
from template.utils import *

from pe_management.decorators.generic import *
from pe_management.forms import *
from pe_management.models import *
from pe_management.settings import *
from pe_management.utils import *


@login_required
def dashboard(request):
    template = "dashboard.html"
    breadcrumbs = {"#": _("Home")}
    return render(request, template, {"breadcrumbs": breadcrumbs})


def download_event_poster(request, event_id):

    event = get_object_or_404(PublicEngagementEvent, pk=event_id)
    data = getattr(event, "data", None)
    
    permission_granted = False

    if event.is_active and event.has_been_approved():
        permission_granted = True

    if not permission_granted:
        if not request.user.is_authenticated:
            raise PermissionDenied()
        
        if request.user.is_superuser:
            permission_granted = True
        elif request.user == event.referent:
            permission_granted = True
        elif request.user == event.created_by:
            permission_granted = True
        elif data and data.involved_personnel == request.user:
            permission_granted = True

        if not permission_granted:
            is_manager = user_in_office(
                user=request.user,
                office_slug_list=[MANAGER_OFFICE]
            )
            if is_manager:
                permission_granted = True

        if not permission_granted:
            is_operator = user_in_office(
                user=request.user,
                office_slug_list=[
                    STRUCTURE_OP_OFFICE, 
                    STRUCTURE_PATRONAGE_OP_OFFICE
                ],
                structure=event.structure,
            )
            if is_operator:
                permission_granted = True

        if not permission_granted:
            raise PermissionDenied()

    if data and data.poster:
        # get folder path
        folder_path = "{}/public-engagement/events/{}".format(
            settings.MEDIA_ROOT,
            event.id
        )
        # get file
        return download_file(
            folder_path,
            os.path.basename(data.poster.name)
        )
    raise Http404
