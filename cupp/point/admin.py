from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django import forms
from django.contrib import messages
from .models import Point, City, District, Type
from cupp.license.models import DimensionTable, DimensionTableLicenseProvider, MainTable
from cupp.event.models import ActionOwner, ActionCategory, StoreDailyLog
from cupp.store_consultant.models import Area, Consultants
from cupp.competitors.models import DimCluster, DimCompType

# Registering models
admin.site.register(City)
admin.site.register(District)
admin.site.register(Type)
admin.site.register(DimensionTable)
admin.site.register(ActionOwner)
admin.site.register(ActionCategory)
admin.site.register(StoreDailyLog)
admin.site.register(DimensionTableLicenseProvider)
admin.site.register(Consultants)
admin.site.register(Area)
admin.site.register(DimCluster)
admin.site.register(DimCompType)


# Custom admin class for the Point model
class PointAdmin(admin.ModelAdmin):
    search_fields = ['id']  # Add 'lat' to the list of fields to search by


admin.site.register(Point, PointAdmin)

# Unregistering the default UserAdmin and registering the custom CUPPUserAdmin
admin.site.unregister(User)


@admin.register(User)
class CUPPUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'groups'),
        }),
    )
    list_display = ('username', 'first_name', 'last_login')
    list_filter = ('is_active', 'groups')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(username='su')

# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from django.contrib.auth.models import User
# from django import forms
# from django.contrib import messages
# from django import forms
# from .models import Point, City, District, Type
# from cupp.license.models import DimensionTable, DimensionTableLicenseProvider, MainTable
# from cupp.event.models import ActionOwner, ActionCategory, StoreDailyLog
# from cupp.store_consultant.models import Area, Consultants
#
# admin.site.register(Point)
# admin.site.unregister(User)
# admin.site.register(City)
# admin.site.register(District)
# admin.site.register(Type)
# admin.site.register(DimensionTable)
# admin.site.register(ActionOwner)
# admin.site.register(ActionCategory)
# admin.site.register(StoreDailyLog)
# admin.site.register(DimensionTableLicenseProvider)
# admin.site.register(Consultants)
# admin.site.register(Area)
#
#
# @admin.register(User)
# class CUPPUserAdmin(UserAdmin):
#     fieldsets = (
#         (None, {'fields': ('username', 'password')}),
#         ('Personal info', {'fields': ('first_name', 'last_name')}),
#         ('Permissions', {
#             'fields': ('is_active', 'is_staff', 'groups'),
#         }),
#     )
#     list_display = ('username', 'first_name', 'last_login')
#     list_filter = ('is_active', 'groups')
#
#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         return qs.exclude(username='su')
