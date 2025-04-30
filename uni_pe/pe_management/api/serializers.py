from rest_framework import serializers

from .. models import PublicEngagementEvent


class PublicEngagementEventLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicEngagementEvent
        fields = ['id', 'title', 'referent', 'structure']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['referent'] = f'{instance.referent}'
        data['structure'] = f'{instance.structure.name}'
        return data


class PublicEngagementEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicEngagementEvent
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['created_by'] = f'{instance.created_by}'
        data['modified_by'] = f'{instance.modified_by}'
        if instance.operator_taken_by:
            data['operator_taken_by'] = f'{instance.operator_taken_by}'
        data['referent'] = f'{instance.referent}'
        data['structure'] = f'{instance.structure.name}'
        data['is_ready_for_request_evaluation'] = instance.is_ready_for_request_evaluation()
        data['can_be_handled_for_evaluation'] = instance.can_be_handled_for_evaluation()
        data['can_be_handled_for_patronage'] = instance.can_be_handled_for_patronage()
        data['is_ready_for_evaluation'] = instance.is_ready_for_evaluation()
        data['is_ready_for_patronage_check'] = instance.is_ready_for_patronage_check()
        data['has_been_approved'] = instance.has_been_approved()
        data['has_been_rejected'] = instance.has_been_rejected()
        data['has_patronage_granted'] = instance.has_patronage_granted()
        data['has_patronage_denied'] = instance.has_patronage_denied()

        return data
