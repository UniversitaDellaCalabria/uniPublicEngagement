import nested_admin

from django import forms
from django.contrib import admin

from .models import *


# Structure Office
class OrganizationalStructureOfficeModelForm(forms.ModelForm):
    class Meta:
        model = OrganizationalStructureOffice
        search = ('namme',)
        fields = ('__all__')


class OrganizationalStructureOfficeInline(admin.TabularInline):
    model = OrganizationalStructureOffice
    form = OrganizationalStructureOfficeModelForm
    extra = 0


# Structure Location
class OrganizationalStructureLocationModelForm(forms.ModelForm):

    class Meta:
        model = OrganizationalStructureLocation
        fields = ('__all__')


class OrganizationalStructureLocationInline(admin.TabularInline):
    model = OrganizationalStructureLocation
    form = OrganizationalStructureLocationModelForm
    extra = 0


# Office employe filter on events
class OrganizationalStructureOfficeEmployeeFilterModelForm(forms.ModelForm):
    class Meta:
        model = OrganizationalStructureOfficeEmployeeFilter
        fields = ('__all__')


class OrganizationalStructureOfficeEmployeeFilterInline(nested_admin.NestedTabularInline):
    model = OrganizationalStructureOfficeEmployeeFilter
    form = OrganizationalStructureOfficeEmployeeFilterModelForm
    extra = 0
    #autocomplete_fields = ('user',)


# Structure Office Employee
class OrganizationalStructureOfficeEmployeeModelForm(forms.ModelForm):

    class Meta:
        model = OrganizationalStructureOfficeEmployee
        fields = ('__all__')


class OrganizationalStructureOfficeEmployeeInline(nested_admin.NestedTabularInline):
    model = OrganizationalStructureOfficeEmployee
    form = OrganizationalStructureOfficeEmployeeModelForm
    extra = 0
    autocomplete_fields = ('employee',)
    inlines = [OrganizationalStructureOfficeEmployeeFilterInline,]


# Structure Location
class OrganizationalStructureOfficeLocationModelForm(forms.ModelForm):

    class Meta:
        model = OrganizationalStructureOfficeLocation
        fields = ('__all__')


class OrganizationalStructureOfficeLocationInline(nested_admin.NestedTabularInline):
    model = OrganizationalStructureOfficeLocation
    form = OrganizationalStructureOfficeLocationModelForm
    extra = 0


# User is structure manager
class UserManageOrganizationalStructureModelForm(forms.ModelForm):
    class Meta:
        model = UserManageOrganizationalStructure
        fields = ('__all__')


class UserManageOrganizationalStructureInline(admin.TabularInline):
    model = UserManageOrganizationalStructure
    form = UserManageOrganizationalStructureModelForm
    extra = 0
    autocomplete_fields = ('user',)

