from django.db.models import Q

from rest_framework import permissions

from ... models import PublicEngagementAnnualMonitoring, PublicEngagementEvent
from .. permissions import IsManager
from . generic import PublicEngagementEventList


class PublicEngagementEventList(PublicEngagementEventList):

    permission_classes = [permissions.IsAuthenticated,
                          IsManager]

    def get_queryset(self, **kwargs):
        """
        """
        events = PublicEngagementEvent.objects\
            .prefetch_related('data', 'report')\
            .select_related('referent', 'structure')\
            .filter(structure__slug=self.kwargs['structure_slug'],
                    structure__is_active=True)

        status = self.request.query_params.get('status')
        if status=='approved':
            events = events.filter(operator_evaluation_success=True,
                                   operator_evaluation_date__isnull=False)
        elif status=='created_by_manager':
            events = events.filter(created_by_manager=True)

        not_eligible = self.request.query_params.get('not_eligible')
        if not_eligible=='true':
            events = events.filter(is_active=False)

        return events
