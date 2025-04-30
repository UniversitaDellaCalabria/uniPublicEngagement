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
