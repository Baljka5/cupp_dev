from django.contrib.admin import AdminSite
from .models import Menu
from django.contrib import admin

class BIReportAdminSite(AdminSite):
    site_header = 'BI Report Admin'
    site_title = 'BI Report Admin Portal'
    index_title = 'Welcome to BI Report Management'

    def has_permission(self, request):
        return request.user.is_active and request.user.is_staff and request.user.groups.filter(name='BIAdmin').exists()

# admin site instance
bi_report_admin_site = BIReportAdminSite(name='bi_report_admin')

# Register models to this site
bi_report_admin_site.register(Menu)
