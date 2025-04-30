from django.contrib import admin


class AbstractCreatedModifiedBySave(object):

    def save_model(self, request, obj, form, change):  # pragma: no cover
        if not request.user.is_authenticated:
            return False

        for field_name in ('created_by', 'modified_by'):
            if not hasattr(obj, field_name):  # pragma: no cover
                continue

            if (field_name == 'modified_by' or not getattr(obj, field_name, None)):
                setattr(obj, field_name, request.user)
        super().save_model(request, obj, form, change)


class AbstractCreatedModifiedBy(AbstractCreatedModifiedBySave, admin.ModelAdmin):
    readonly_fields = ('created_by', 'modified_by')
