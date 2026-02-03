from django.db.models import Count, Q
from rest_framework import generics, permissions
from rest_framework.response import Response

from ...models import (
    PublicEngagementEvent,
    PublicEngagementEventData,
    PublicEngagementEventScientificArea,
)
from ..permissions import IsStructureEvaluationOperator
from .generic import PublicEngagementEventList


class PublicEngagementEventList(PublicEngagementEventList):
    permission_classes = [permissions.IsAuthenticated, IsStructureEvaluationOperator]


class PublicEngagementEventTypesList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsStructureEvaluationOperator]

    def get_queryset(self, **kwargs):
        if not kwargs.get("structure"):
            return []
        if not kwargs.get("year"):
            return []
        events = (
            PublicEngagementEventData.objects.filter(
                event__structure__slug=kwargs.get("structure"),
                event__structure__is_active=True,
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

    def get(self, request, structure_slug):
        return Response(
            self.get_queryset(year=request.GET.get("year"), structure=structure_slug)
        )


class PublicEngagementMainProjectsList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsStructureEvaluationOperator]

    def get_queryset(self, **kwargs):
        if not kwargs.get("structure"):
            return []
        if not kwargs.get("year"):
            return []
        events = (
            PublicEngagementEventData.objects.filter(
                event__structure__slug=kwargs.get("structure"),
                event__structure__is_active=True,
                event__is_active=True,
                event__operator_evaluation_success=True,
                event__operator_evaluation_date__isnull=False,
                event__start__year=kwargs["year"],
                project_name__isnull=False,
            )
            .values("project_name__title")
            .annotate(num=Count("id"))
            .order_by("-num")
        )
        return events

    def get(self, request, structure_slug):
        return Response(
            self.get_queryset(year=request.GET.get("year"), structure=structure_slug)
        )


class PublicEngagementEventsRecipientsList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsStructureEvaluationOperator]

    def get_queryset(self, **kwargs):
        if not kwargs.get("structure"):
            return []
        if not kwargs.get("year"):
            return []
        events = (
            PublicEngagementEventData.objects.filter(
                event__structure__slug=kwargs.get("structure"),
                event__structure__is_active=True,
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

    def get(self, request, structure_slug):
        return Response(
            self.get_queryset(year=request.GET.get("year"), structure=structure_slug)
        )


class PublicEngagementEventsTargetsList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsStructureEvaluationOperator]

    def get_queryset(self, **kwargs):
        if not kwargs.get("structure"):
            return []
        if not kwargs.get("year"):
            return []
        events = (
            PublicEngagementEventData.objects.filter(
                event__structure__slug=kwargs.get("structure"),
                event__structure__is_active=True,
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

    def get(self, request, structure_slug):
        return Response(
            self.get_queryset(year=request.GET.get("year"), structure=structure_slug)
        )


class PublicEngagementEventsMethodsOfExecutionList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsStructureEvaluationOperator]

    def get_queryset(self, **kwargs):
        if not kwargs.get("structure"):
            return []
        if not kwargs.get("year"):
            return []
        events = (
            PublicEngagementEventData.objects.filter(
                event__structure__slug=kwargs.get("structure"),
                event__structure__is_active=True,
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

    def get(self, request, structure_slug):
        return Response(
            self.get_queryset(year=request.GET.get("year"), structure=structure_slug)
        )


class PublicEngagementEventsGeographicalDimensionList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsStructureEvaluationOperator]

    def get_queryset(self, **kwargs):
        if not kwargs.get("structure"):
            return []
        if not kwargs.get("year"):
            return []
        events = (
            PublicEngagementEventData.objects.filter(
                event__structure__slug=kwargs.get("structure"),
                event__structure__is_active=True,
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

    def get(self, request, structure_slug):
        return Response(
            self.get_queryset(year=request.GET.get("year"), structure=structure_slug)
        )


class PublicEngagementEventsOrganizingSubjectList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsStructureEvaluationOperator]

    def get_queryset(self, **kwargs):
        if not kwargs.get("structure"):
            return []
        if not kwargs.get("year"):
            return []
        events = (
            PublicEngagementEventData.objects.filter(
                event__structure__slug=kwargs.get("structure"),
                event__structure__is_active=True,
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

    def get(self, request, structure_slug):
        return Response(
            self.get_queryset(year=request.GET.get("year"), structure=structure_slug)
        )


class PublicEngagementEventsPromoChannelList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsStructureEvaluationOperator]

    def get_queryset(self, **kwargs):
        if not kwargs.get("structure"):
            return []
        if not kwargs.get("year"):
            return []
        events = (
            PublicEngagementEventData.objects.filter(
                event__structure__slug=kwargs.get("structure"),
                event__structure__is_active=True,
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

    def get(self, request, structure_slug):
        return Response(
            self.get_queryset(year=request.GET.get("year"), structure=structure_slug)
        )


class PublicEngagementEventsPatronageRequestedList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsStructureEvaluationOperator]

    def get_queryset(self, **kwargs):
        if not kwargs.get("structure"):
            return []
        if not kwargs.get("year"):
            return []
        events = (
            PublicEngagementEventData.objects.filter(
                event__structure__slug=kwargs.get("structure"),
                event__structure__is_active=True,
                event__is_active=True,
                event__operator_evaluation_success=True,
                event__operator_evaluation_date__isnull=False,
                event__start__year=kwargs["year"],
            )
            .values("patronage_requested")
            .annotate(num=Count("id"))
        )
        return events

    def get(self, request, structure_slug):
        return Response(
            self.get_queryset(year=request.GET.get("year"), structure=structure_slug)
        )


class PublicEngagementEventsMonitoringDataProvidedList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsStructureEvaluationOperator]

    def get_queryset(self, **kwargs):
        if not kwargs.get("structure"):
            return []
        if not kwargs.get("year"):
            return []
        return PublicEngagementEvent.objects.filter(
            structure__slug=kwargs.get("structure"),
            structure__is_active=True,
            is_active=True,
            operator_evaluation_success=True,
            operator_evaluation_date__isnull=False,
            start__year=kwargs["year"],
        ).aggregate(
            yes=Count("id", filter=Q(report__isnull=False), distinct=True),
            no=Count("id", filter=Q(report__isnull=True)),
        )

    def get(self, request, structure_slug):
        return Response(
            self.get_queryset(year=request.GET.get("year"), structure=structure_slug)
        )


class PublicEngagementEventsImpactEvaluationList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsStructureEvaluationOperator]

    def get_queryset(self, **kwargs):
        if not kwargs.get("structure"):
            return []
        if not kwargs.get("year"):
            return []
        return PublicEngagementEvent.objects.filter(
            structure__slug=kwargs.get("structure"),
            structure__is_active=True,
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

    def get(self, request, structure_slug):
        return Response(
            self.get_queryset(year=request.GET.get("year"), structure=structure_slug)
        )


class PublicEngagementEventsScientificAreasList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsStructureEvaluationOperator]

    def get_queryset(self, **kwargs):
        if not kwargs.get("structure"):
            return []
        if not kwargs.get("year"):
            return []
        return PublicEngagementEventScientificArea.objects.annotate(
            number=Count(
                "publicengagementeventreport",
                filter=Q(
                    publicengagementeventreport__event__structure__slug=kwargs.get(
                        "structure"
                    ),
                    publicengagementeventreport__event__structure__is_active=True,
                    publicengagementeventreport__event__is_active=True,
                    publicengagementeventreport__event__operator_evaluation_success=True,
                    publicengagementeventreport__event__operator_evaluation_date__isnull=False,
                    publicengagementeventreport__event__start__year=kwargs["year"],
                ),
            )
        ).values("description", "number")

    def get(self, request, structure_slug):
        return Response(
            self.get_queryset(year=request.GET.get("year"), structure=structure_slug)
        )
