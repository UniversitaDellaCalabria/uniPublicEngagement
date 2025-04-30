from django.contrib.auth import get_user_model
from django_filters.rest_framework import *

from rest_framework import filters, generics, permissions

from template.api.pagination import CustomPagination

from .. models import OrganizationalStructure
from . serializers import *


class OrganizationalStructureList(generics.ListAPIView):

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrganizationalStructureSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter]
    search_fields = ['name','unique_code']
    pagination_class = CustomPagination
    ordering = ['name']
    queryset = OrganizationalStructure.objects.filter(is_active=True)


class OrganizationalStructureDetail(generics.RetrieveAPIView):

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrganizationalStructureSerializer
    queryset = OrganizationalStructure.objects.filter(is_active=True)
