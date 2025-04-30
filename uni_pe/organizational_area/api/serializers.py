from rest_framework import serializers

from .. models import OrganizationalStructure


class OrganizationalStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationalStructure
        fields = ['id', 'name', 'unique_code']
