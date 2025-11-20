from django.db.models import Count

from rest_framework import generics, permissions
from rest_framework.response import Response

from ... models import *
from .. permissions import IsManager
from . generic import PublicEngagementEventList


class PublicEngagementEventList(PublicEngagementEventList):
    permission_classes = [permissions.IsAuthenticated, IsManager]


class PublicEngagementEventStructureCounterList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def get_queryset(self, **kwargs):
        events = PublicEngagementEvent.objects\
            .values("structure__name")\
            .annotate(num_iniziative=Count("id"))\
            .order_by("structure__name")
        return events

    def get(self, request):
        return Response(self.get_queryset())


class PublicEngagementEventTypesList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def get_queryset(self, **kwargs):
        events = PublicEngagementEventData.objects\
            .values("event_type__description")\
            .annotate(num_iniziative=Count("id"))\
            .order_by("event_type__description")
        return events

    def get(self, request):
        return Response(self.get_queryset())


class PublicEngagementMainProjectsList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def get_queryset(self, **kwargs):
        events = PublicEngagementEventData.objects\
            .filter(project_name__isnull=False)\
            .values("project_name__title")\
            .annotate(num_iniziative=Count("id"))\
            .order_by("project_name__title")
        return events

    def get(self, request):
        return Response(self.get_queryset())


class PublicEngagementEventsRecipientsList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def get_queryset(self, **kwargs):
        events = PublicEngagementEventData.objects\
            .values("recipient__description")\
            .annotate(num_iniziative=Count("id"))\
            .order_by("recipient__description")
        return events

    def get(self, request):
        return Response(self.get_queryset())


class PublicEngagementEventsTargetsList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def get_queryset(self, **kwargs):
        events = PublicEngagementEventData.objects\
            .filter(target__isnull=False)\
            .values("target__description")\
            .annotate(num_iniziative=Count("id"))\
            .order_by("target__description")
        return events

    def get(self, request):
        return Response(self.get_queryset())


class PublicEngagementEventsMethodsOfExecutionList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def get_queryset(self, **kwargs):
        events = PublicEngagementEventData.objects\
            .filter(method_of_execution__isnull=False)\
            .values("method_of_execution__description")\
            .annotate(num_iniziative=Count("id"))\
            .order_by("method_of_execution__description")
        return events

    def get(self, request):
        return Response(self.get_queryset())
