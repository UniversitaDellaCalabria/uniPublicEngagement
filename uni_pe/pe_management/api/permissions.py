
from organizational_area.models import OrganizationalStructure

from rest_framework.permissions import BasePermission

from .. utils import (user_is_operator,
                      user_is_patronage_operator,
                      user_is_manager)


class IsStructureEvaluationOperator(BasePermission):
    def has_permission(self, request, view):
        structure_slug = view.kwargs.get('structure_slug', None)
        if not structure_slug:
            return False
        structure = OrganizationalStructure.objects.filter(slug=structure_slug,
                                                           is_active=True).first()
        if not structure:
            return False
        if user_is_operator(user=request.user, structure=structure):
            return True
        return False


class IsStructurePatronageOperator(BasePermission):
    def has_permission(self, request, view):
        structure_slug = view.kwargs.get('structure_slug', None)
        if not structure_slug:
            return False
        structure = OrganizationalStructure.objects.filter(slug=structure_slug,
                                                           is_active=True).first()
        if not structure:
            return False
        if user_is_patronage_operator(user=request.user, structure=structure):
            return True
        return False


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return user_is_manager(request.user)
