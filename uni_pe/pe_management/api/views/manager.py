from django.db.models import Count, Q, Avg
from django.db.models.functions import Round
from rest_framework import generics, permissions
from rest_framework.response import Response

from ...models import (
    PublicEngagementEvent,
    PublicEngagementEventData,
    PublicEngagementEventScientificArea,
    PublicEngagementEventReport
)
from ..permissions import IsManager
from .generic import PublicEngagementEventList


class PublicEngagementEventList(PublicEngagementEventList):
    permission_classes = [permissions.IsAuthenticated, IsManager]


class PublicEngagementEventStructureCounterList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def get_queryset(self, **kwargs):
        if not kwargs.get("year"):
            return []
        events = (
            PublicEngagementEvent.objects.filter(
                is_active=True,
                operator_evaluation_success=True,
                operator_evaluation_date__isnull=False,
                start__year=kwargs["year"],
            )
            .values("structure__slug")
            .annotate(num=Count("id"))
            .order_by("-num")
        )
        return events

    def get(self, request):
        return Response(self.get_queryset(year=request.GET.get("year")))


class PublicEngagementEventTypesList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def get_queryset(self, **kwargs):
        if not kwargs.get("year"):
            return []
        events = (
            PublicEngagementEventData.objects.filter(
                event__is_active=True,
                event__operator_evaluation_success=True,
                event__operator_evaluation_date__isnull=False,
                event__start__year=kwargs["year"],
            )
            .values("event_type__description")
            .annotate(num=Count("id"))
            .order_by("-num")
        )
        return events

    def get(self, request):
        return Response(self.get_queryset(year=request.GET.get("year")))


class PublicEngagementMainProjectsList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def get_queryset(self, **kwargs):
        if not kwargs.get("year"):
            return []
        events = (
            PublicEngagementEventData.objects.filter(
                event__is_active=True,
                event__operator_evaluation_success=True,
                event__operator_evaluation_date__isnull=False,
                event__start__year=kwargs["year"],
                # PROJECT NAME TEMPORARY MOD
                # project_name__isnull=False,
                project_full_name__isnull=False,
                # END PROJECT NAME TEMPORARY MOD
            )
            # PROJECT NAME TEMPORARY MOD
            # .values("project_name__title")
            # .annotate(num=Count("id"))
            .values("project_name")
            .annotate(num=Count("project_name"))
            # END PROJECT NAME TEMPORARY MOD
            .order_by("-num")
        )
        return events

    def get(self, request):
        return Response(self.get_queryset(year=request.GET.get("year")))


class PublicEngagementEventsRecipientsList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def get_queryset(self, **kwargs):
        if not kwargs.get("year"):
            return []
        events = (
            PublicEngagementEventData.objects.filter(
                event__is_active=True,
                event__operator_evaluation_success=True,
                event__operator_evaluation_date__isnull=False,
                event__start__year=kwargs["year"],
            )
            .values("recipient__description")
            .annotate(num=Count("id"))
            .order_by("-num")
        )
        return events

    def get(self, request):
        return Response(self.get_queryset(year=request.GET.get("year")))


class PublicEngagementEventsTargetsList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def get_queryset(self, **kwargs):
        if not kwargs.get("year"):
            return []
        events = (
            PublicEngagementEventData.objects.filter(
                event__is_active=True,
                event__operator_evaluation_success=True,
                event__operator_evaluation_date__isnull=False,
                event__start__year=kwargs["year"],
                target__isnull=False,
            )
            .values("target__description")
            .annotate(num=Count("id"))
            .order_by("target__id")
        )
        return events

    def get(self, request):
        return Response(self.get_queryset(year=request.GET.get("year")))


class PublicEngagementEventsMethodsOfExecutionList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def get_queryset(self, **kwargs):
        if not kwargs.get("year"):
            return []
        events = (
            PublicEngagementEventData.objects.filter(
                event__is_active=True,
                event__operator_evaluation_success=True,
                event__operator_evaluation_date__isnull=False,
                event__start__year=kwargs["year"],
                method_of_execution__isnull=False,
            )
            .values("method_of_execution__description")
            .annotate(num=Count("id"))
            .order_by("-num")
        )
        return events

    def get(self, request):
        return Response(self.get_queryset(year=request.GET.get("year")))


class PublicEngagementEventsGeographicalDimensionList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def get_queryset(self, **kwargs):
        if not kwargs.get("year"):
            return []
        events = (
            PublicEngagementEventData.objects.filter(
                event__is_active=True,
                event__operator_evaluation_success=True,
                event__operator_evaluation_date__isnull=False,
                event__start__year=kwargs["year"],
                geographical_dimension__isnull=False,
            )
            .values("geographical_dimension")
            .annotate(num=Count("id"))
            .order_by("geographical_dimension")
        )
        return events

    def get(self, request):
        return Response(self.get_queryset(year=request.GET.get("year")))


class PublicEngagementEventsOrganizingSubjectList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def get_queryset(self, **kwargs):
        if not kwargs.get("year"):
            return []
        events = (
            PublicEngagementEventData.objects.filter(
                event__is_active=True,
                event__operator_evaluation_success=True,
                event__operator_evaluation_date__isnull=False,
                event__start__year=kwargs["year"],
                organizing_subject__isnull=False,
            )
            .values("organizing_subject")
            .annotate(num=Count("id"))
            .order_by("organizing_subject")
        )
        return events

    def get(self, request):
        return Response(self.get_queryset(year=request.GET.get("year")))


class PublicEngagementEventsPromoChannelList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def get_queryset(self, **kwargs):
        if not kwargs.get("year"):
            return []
        events = (
            PublicEngagementEventData.objects.filter(
                event__is_active=True,
                event__operator_evaluation_success=True,
                event__operator_evaluation_date__isnull=False,
                event__start__year=kwargs["year"],
            )
            .values("promo_channel__description")
            .annotate(num=Count("id"))
            .order_by("promo_channel__description")
        )
        return events

    def get(self, request):
        return Response(self.get_queryset(year=request.GET.get("year")))


class PublicEngagementEventsPatronageRequestedList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def get_queryset(self, **kwargs):
        if not kwargs.get("year"):
            return []
        return PublicEngagementEventData.objects.filter(
            event__is_active=True,
            event__operator_evaluation_success=True,
            event__operator_evaluation_date__isnull=False,
            event__start__year=kwargs["year"],
        ).aggregate(
            yes=Count("id", filter=Q(patronage_requested=True), distinct=True),
            no=Count("id", filter=Q(patronage_requested=False)),
        )

    def get(self, request):
        return Response(self.get_queryset(year=request.GET.get("year")))


class PublicEngagementEventsMonitoringDataProvidedList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def get_queryset(self, **kwargs):
        if not kwargs.get("year"):
            return []
        return PublicEngagementEvent.objects.filter(
            is_active=True,
            operator_evaluation_success=True,
            operator_evaluation_date__isnull=False,
            start__year=kwargs["year"],
        ).aggregate(
            yes=Count("id", filter=Q(report__isnull=False), distinct=True),
            no=Count("id", filter=Q(report__isnull=True)),
        )

    def get(self, request):
        return Response(self.get_queryset(year=request.GET.get("year")))


class PublicEngagementEventsImpactEvaluationList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def get_queryset(self, **kwargs):
        if not kwargs.get("year"):
            return []
        return PublicEngagementEvent.objects.filter(
            is_active=True,
            operator_evaluation_success=True,
            operator_evaluation_date__isnull=False,
            start__year=kwargs["year"],
        ).aggregate(
            yes=Count(
                "id",
                filter=Q(report__isnull=False, report__impact_evaluation=True),
                distinct=True,
            ),
            no=Count(
                "id",
                filter=Q(report__isnull=True)
                | Q(report__isnull=False, report__impact_evaluation=False),
            ),
        )

    def get(self, request):
        return Response(self.get_queryset(year=request.GET.get("year")))


class PublicEngagementEventsScientificAreasList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def get_queryset(self, **kwargs):
        if not kwargs.get("year"):
            return []
        return PublicEngagementEventScientificArea.objects.annotate(
            number=Count(
                "publicengagementeventreport",
                filter=Q(
                    publicengagementeventreport__event__is_active=True,
                    publicengagementeventreport__event__operator_evaluation_success=True,
                    publicengagementeventreport__event__operator_evaluation_date__isnull=False,
                    publicengagementeventreport__event__start__year=kwargs["year"],
                ),
            )
        ).values("description", "number")

    def get(self, request):
        return Response(self.get_queryset(year=request.GET.get("year")))


class PublicEngagementEventCollaboratorTypesList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def get_queryset(self, **kwargs):
        if not kwargs.get("year"):
            return []
        events = (
            PublicEngagementEventReport.objects.filter(
                event__is_active=True,
                event__operator_evaluation_success=True,
                event__operator_evaluation_date__isnull=False,
                event__start__year=kwargs["year"],
                collaborator_type__isnull=False,
            )
            .values("collaborator_type__description")
            .annotate(num=Count("id"))
            .order_by("collaborator_type__description")
        )
        return events

    def get(self, request):
        return Response(self.get_queryset(year=request.GET.get("year")))

        
class PublicEngagementEventInvolvedPersonnelList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]
        
    def get_queryset(self, **kwargs):
        if not kwargs.get("year"):
            return []
        events = (
            PublicEngagementEventData.objects.filter(
                event__is_active=True,
                event__operator_evaluation_success=True,
                event__operator_evaluation_date__isnull=False,
                event__start__year=kwargs["year"],
                involved_personnel__isnull=False,
            )
            .values(
                "involved_personnel__last_name",
                "involved_personnel__first_name", 
            )
            .annotate(num=Count("id"))
            .order_by("-num", "involved_personnel__last_name")
        )
        return events

    def get(self, request):
        return Response(self.get_queryset(year=request.GET.get("year")))

        
class PublicEngagementEventInvolvedStructuresList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]
        
    def get_queryset(self, **kwargs):
        if not kwargs.get("year"):
            return []
        events = (
            PublicEngagementEventData.objects.filter(
                event__is_active=True,
                event__operator_evaluation_success=True,
                event__operator_evaluation_date__isnull=False,
                event__start__year=kwargs["year"],
                involved_structure__isnull=False,
            )
            .values(
                "involved_structure__name", 
            )
            .annotate(num=Count("id"))
            .order_by("-num", "involved_structure__name")
        )
        return events

    def get(self, request):
        return Response(self.get_queryset(year=request.GET.get("year")))


class PublicEngagementEventAudience(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]
        
    def get_queryset(self, **kwargs):
        if not kwargs.get("year"):
            return []
        events = (
            PublicEngagementEventReport.objects.filter(
                event__is_active=True,
                event__operator_evaluation_success=True,
                event__operator_evaluation_date__isnull=False,
                event__start__year=kwargs["year"],
            )
            .aggregate(value=Round(Avg('participants')))
        )
        return events

    def get(self, request):
        return Response(self.get_queryset(year=request.GET.get("year")))


class PublicEngagementEventRerefentsList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]
        
    def get_queryset(self, **kwargs):
        if not kwargs.get("year"):
            return []
        events = (
            PublicEngagementEvent.objects.filter(
                is_active=True,
                operator_evaluation_success=True,
                operator_evaluation_date__isnull=False,
                start__year=kwargs["year"],
            )
            .values(
                "referent__last_name",
                "referent__first_name", 
            )
            .annotate(num=Count("id"))
            .order_by("-num", "referent__last_name")
        )
        return events

    def get(self, request):
        return Response(self.get_queryset(year=request.GET.get("year")))
