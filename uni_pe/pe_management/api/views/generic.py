from django.db.models import Q
from django_filters.rest_framework import *

from organizational_area.api.views import *

from rest_framework import filters, generics, permissions

from template.api.pagination import CustomPagination

from ... utils import *
from .. filters import PublicEngagementEventFilter
from .. serializers import *


class PublicEngagementEventList(generics.ListAPIView):

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PublicEngagementEventSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter]
    filterset_class =  PublicEngagementEventFilter
    search_fields = ['title', 'referent__last_name', 'structure__name']
    pagination_class = CustomPagination
    ordering_fields = ['start', 'end', 'title', 'referent__last_name']
    ordering = ['-start']

    def get_queryset(self, **kwargs):
        events = PublicEngagementEvent.objects\
            .prefetch_related('data', 'report')\
            .select_related('referent', 'structure')\
            .filter(structure__slug=self.kwargs['structure_slug'],
                    structure__is_active=True)

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
                to_evaluate=True
            )
        elif status=='to_evaluate':
            events = events.filter(
                years_query,
                operator_taken_date__isnull=False,
                operator_evaluation_date__isnull=True,
                created_by_manager=False,
                to_evaluate=True
            )
        elif status=='draft':
            events = events.filter(to_evaluate=False)
        elif status=='approved':
            events = events.filter(operator_evaluation_success=True,
                                   operator_evaluation_date__isnull=False,
                                   to_evaluate=True)
        elif status=='rejected':
            events = events.filter(operator_evaluation_success=False,
                                   operator_evaluation_date__isnull=False,
                                   to_evaluate=True)
        # ~ elif status=='not_eligible':
            # ~ events = events.filter(is_active=False)
        elif status=='created_by_manager':
            events = events.filter(created_by_manager=True)

        not_eligible = self.request.query_params.get('not_eligible')
        if not_eligible=='true':
            events = events.filter(is_active=False)

        return events


class PublicEngagementApprovedEventList(PublicEngagementEventList):
    serializer_class = PublicEngagementEventLiteSerializer

    def get_queryset(self, **kwargs):
        """
        """
        events = PublicEngagementEvent.objects\
            .prefetch_related('data', 'report')\
            .select_related('referent', 'structure')\
            .filter(structure__is_active=True,
                    operator_evaluation_success=True)

        return events


class PublicEngagementApprovedEventDetail(generics.RetrieveAPIView):
    serializer_class = PublicEngagementEventLiteSerializer
    queryset = PublicEngagementEvent.objects.all()


class OrganizationalStructureList(OrganizationalStructureList):
    permission_classes = [permissions.IsAuthenticated]
    queryset = OrganizationalStructure.objects.filter(is_active=True)
