from django.db.models import Q


from rest_framework import permissions

from ... models import PublicEngagementEvent

# from .. permissions import *

from . generic import PublicEngagementEventList


class PublicEngagementEventList(PublicEngagementEventList):

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self, **kwargs):
        """
        """
        events = PublicEngagementEvent.objects\
            .prefetch_related('data', 'report')\
            .select_related('referent', 'structure')\
            .filter(data__involved_personnel=self.request.user,
                    structure__is_active=True,
                    # ~ is_active=True,
                    operator_evaluation_date__isnull=False)
                    # ~ operator_evaluation_success=True)
        return events
