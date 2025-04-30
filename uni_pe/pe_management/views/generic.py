from django.conf import settings

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, reverse
from django.utils.translation import gettext_lazy as _

from organizational_area.models import *
from organizational_area.utils import user_in_office

from template.utils import *

from .. decorators.generic import *
from .. forms import *
from .. models import *
from .. settings import *
from .. utils import *


@login_required
def dashboard(request):
    template = 'dashboard.html'
    breadcrumbs = {'#': _('Public Engagement')}
    return render(request, template, {'breadcrumbs': breadcrumbs})


@login_required
def download_event_poster(request, event_id):
    event = get_object_or_404(PublicEngagementEvent, pk=event_id)
    permission_granted = False

    if request.user.is_superuser: permission_granted = True
    elif request.user == event.referent: permission_granted = True
    elif request.user == event.created_by: permission_granted = True

    data = getattr(event, 'data', None)
    if data and data.involved_personnel == request.user and event.operator_evaluation_date and event.operator_evaluation_success:
        permission_granted = True

    if not permission_granted:
        is_manager = user_in_office([MANAGER_OFFICE])
        if is_manager: permission_granted = True

    if not permission_granted:
        is_operator = user_in_office([OPERATOR_OFFICE, PATRONAGE_OFFICE],
                                     event.structure)
        if is_operator: permission_granted = True

    if not permission_granted:
        raise Http403

    data = getattr(event, 'data', None)
    if data and data.poster:
        # get folder path
        folder_path = "{}/public-engagement/events/{}".format(settings.MEDIA_ROOT,
                                                              event.id)
        # get file
        return download_file(folder_path, os.path.basename(data.poster.name))
    raise Http404

