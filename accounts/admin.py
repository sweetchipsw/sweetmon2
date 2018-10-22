from django.contrib import admin
from django.conf import settings
from .models import Profile
from django.db.models import Q


def get_all_field_names(Model):
    return [f.name for f in Model._meta.get_fields()]


def exceptfield(list_display, fields=[]):
    # Remove fields that you won't show.
    if len(fields) == 0:
        return 0
    for field in fields:
        list_display.remove(field)


class ProfileAdmin(admin.ModelAdmin):
    list_display = get_all_field_names(Profile)
    exceptfield(list_display, ["api_key"])

    readonly_fields = ('api_key',)

    def get_queryset(self, request):
        fields = super(self.__class__, self).get_queryset(request)
        fields = fields.filter(owner_id=request.user)
        return fields

    def get_fieldsets(self, request, obj=None):
        fields = super(self.__class__, self).get_fieldsets(request, obj)
        fields[0][1]['fields'].remove('owner')  # Hide field
        return fields

    def save_model(self, request, instance, form, change):
        user = request.user
        instance = form.save(commit=False)
        if not change or not instance.owner:
            instance.owner = user  # set owner
        instance.save()
        form.save_m2m()
        return instance


admin.site.register(Profile, ProfileAdmin)
