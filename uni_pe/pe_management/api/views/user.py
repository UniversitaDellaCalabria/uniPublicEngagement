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
            .filter(Q(referent=self.request.user) |
                    Q(created_by=self.request.user),
                    structure__is_active=True)

        status = self.request.query_params.get('status')
        if status=='approved':
            events = events.filter(operator_evaluation_success=True,
                                   operator_evaluation_date__isnull=False)
        elif status=='rejected':
            events = events.filter(operator_evaluation_success=False,
                                   operator_evaluation_date__isnull=False)

        not_eligible = self.request.query_params.get('not_eligible')
        if not_eligible=='true':
            events = events.filter(is_active=False)

        return events
