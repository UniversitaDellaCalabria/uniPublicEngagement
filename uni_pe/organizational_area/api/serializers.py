from rest_framework import serializers

from ..models import OrganizationalStructure


class OrganizationalStructureSerializer(serializers.ModelSerializer):
    # unique_code = serializers.SerializerMethodField()

    class Meta:
        model = OrganizationalStructure
        fields = ["id", "name", "unique_code"]

    # def get_unique_code(self, obj):
    #     return obj.unique_code.upper()
