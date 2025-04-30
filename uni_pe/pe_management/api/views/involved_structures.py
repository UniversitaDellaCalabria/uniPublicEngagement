from django.db.models import Q

from rest_framework import permissions

from ... models import PublicEngagementAnnualMonitoring, PublicEngagementEvent
from .. permissions import IsStructureEvaluationOperator
from . generic import PublicEngagementEventList


class PublicEngagementEventList(PublicEngagementEventList):

    permission_classes = [permissions.IsAuthenticated,
                          IsStructureEvaluationOperator]

    def get_queryset(self, **kwargs):
        """
        """
        events = PublicEngagementEvent.objects\
            .prefetch_related('data', 'report')\
            .select_related('referent', 'structure')\
            .filter(data__involved_structure__slug=self.kwargs['structure_slug'],
                    data__involved_structure__is_active=True,
                    structure__is_active=True,
                    to_evaluate=True,
                    operator_evaluation_date__isnull=False)
                    #is_active=True)

        status = self.request.query_params.get('status')
        if status=='approved':
            events = events.filter(operator_evaluation_success=True,
                                   operator_evaluation_date__isnull=False)
        elif status=='rejected':
            events = events.filter(operator_evaluation_success=False,
                                   operator_evaluation_date__isnull=False)
        return events
