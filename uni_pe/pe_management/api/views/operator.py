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
            .filter(structure__slug=self.kwargs['structure_slug'],
                    structure__is_active=True,
                    to_evaluate=True)

        status = self.request.query_params.get('status')
        if status=='to_handle' or status=='to_evaluate':
            active_years = PublicEngagementAnnualMonitoring.objects\
                                                   .filter(is_active=True)\
                                                   .values_list('year', flat=True)
            years_query = Q()
            for year in active_years:
                years_query |= Q(start__year=year)
        if status=='to_handle':
            events = events.filter(
                years_query,
                operator_taken_date__isnull=True,
                created_by_manager=False,
            )
        elif status=='to_evaluate':
            events = events.filter(
                years_query,
                operator_taken_date__isnull=False,
                operator_evaluation_date__isnull=True,
                created_by_manager=False,
            )
        elif status=='approved':
            events = events.filter(operator_evaluation_success=True,
                                   operator_evaluation_date__isnull=False)
        elif status=='rejected':
            events = events.filter(operator_evaluation_success=False,
                                   operator_evaluation_date__isnull=False)

        not_eligible = self.request.query_params.get('not_eligible')
        if not_eligible=='true':
            events = events.filter(is_active=False)

        return events
