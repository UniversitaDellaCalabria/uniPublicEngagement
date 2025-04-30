import django_filters
from .. models import PublicEngagementEvent


class PublicEngagementEventFilter(django_filters.FilterSet):
    class Meta:
        model = PublicEngagementEvent
        fields = {
            'title': ['exact', 'icontains'],
            'start': ['year'],
            'end': ['year'],
            'referent__last_name': ['exact','icontains'],
            'to_evaluate': ['exact'],
            'operator_evaluation_success': ['exact'],
            'structure__name': ['icontains']
        }
