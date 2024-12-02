"""
xbook URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from django.contrib.auth import views as auth_views
from cupp.common import views as common_views
from cupp.point import views as point_views
from cupp.point.views import get_districts, custom_login_redirect
from cupp.license import views_lic as license_views
from cupp.event import views_event as event_views
from cupp.rent import views_rent as rent_views
from cupp.store_consultant import views as sc_views
from cupp.store_trainer import views as st_views
from cupp.competitors import views as comp_views
from cupp.master_api.views import StoreMasterAPI
from cupp.veritech_api.views import fetch_and_save_employee_data
from cupp.dispute import views as leg_views
# from cupp.powerBI_api.views import fetch_powerbi_data

# from cupp.ajax_table_list import ajax_table_list

urlpatterns = [

    path('save/', fetch_and_save_employee_data, name='save_employee_data'),
    # path('power/', fetch_powerbi_data, name='save_powerbi_data'),

    path('api/storemaster/', StoreMasterAPI.as_view(), name='storemaster-api'),

    path('ajax/get_districts/', get_districts, name='ajax_get_districts'),
    path('', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),

    # path('ajax/table-data/', ajax_table_list.get_table_data, name='ajax_table_data'),

    path('custom-login-redirect/', custom_login_redirect, name='custom_login_redirect'),

    path('groups/', point_views.display_groups, name='display-groups'),
    path('bi-embed/', point_views.bi_embed, name='bi-embed'),
    path('', point_views.index, name='event_index'),
    # path('register-license/', license_views.MainTableCreateView, name='register_license'),

    path('leg-index/', leg_views.index, name='leg-index'),
    path('leg-add/', leg_views.leg_add, name='leg-add'),
    path('leg-edit/<int:id>', leg_views.edit, name='leg-edit'),
    path('leg-update/<int:id>', leg_views.update, name='leg-update'),
    path('leg-delete/<int:id>', leg_views.destroy, name='leg-delete'),

    path('get-unallocated-stores/', sc_views.get_unallocated_stores, name='get_unallocated_stores'),

    path('sc-index/', sc_views.scIndex, name='sc-index'),
    path('store-index/', sc_views.index, name='store-index'),
    path('sc-view/<int:id>', sc_views.sc_view, name='sc-views'),
    path('sc-edit/<int:id>', sc_views.edit, name='sc-edit'),
    path('sc-update/<int:id>', sc_views.update, name='sc-update'),
    path('update_consultant_area/', sc_views.update_consultant_area, name='update_consultant_area'),
    # path('update_allocation/', sc_views.update_allocation, name='update_allocation'),
    path('save-allocations/', sc_views.save_allocations, name='save_allocations'),
    path('get-allocations/', sc_views.get_allocations, name='get_allocations'),
    path('get-team-data/<int:team_id>/', sc_views.get_team_data, name='get_team_data'),
    path('get-scs-by-team/<int:team_id>/', sc_views.get_scs_by_team, name='get_scs_by_team'),

    path('save-consultant-stores/', sc_views.save_consultant_stores, name='save-consultant-stores'),

    path('log-index/', event_views.index, name='event_index'),
    path('log-create', event_views.event_addnew, name='event-create'),
    path('log-edit/<int:id>', event_views.edit, name='event-edit'),
    path('log-update/<int:id>', event_views.update, name='event_update'),
    path('log-delete/<int:id>', event_views.destroy, name='log-delete'),

    path('comp-index/', comp_views.index, name='comp_index'),
    path('comp-create/', comp_views.comp_addnew, name='comp-create'),
    path('comp-edit/<int:id>', comp_views.edit, name='comp-edit'),
    path('comp-update/<int:id>', comp_views.update, name='comp_update'),
    path('comp-delete/<int:id>', comp_views.destroy, name='comp-delete'),

    path('rent-index/', rent_views.index, name='rent_index'),
    path('rent-create', rent_views.rent_addnew, name='rent-create'),
    path('rent-edit/<int:id>', rent_views.edit, name='rent-edit'),
    path('rent-update/<int:id>', rent_views.update, name='rent-update'),
    path('rent-delete/<int:id>', rent_views.destroy, name='rent-delete'),
    path('api/store-id-search/', rent_views.store_id_search, name='store_id_search'),

    path('st-index/', st_views.index, name='st-index'),
    path('st-view/<int:id>', st_views.st_view, name='st-view'),
    path('st-edit/<int:id>', st_views.edit, name='st-edit'),
    path('st-update/<int:id>', st_views.update, name='st-update'),
    # path('st-delete/<int:id>', st_views.destroy, name='st-delete'),

    path('register-license/', license_views.index, name='index'),
    path('addnew', license_views.addnew, name='addnew'),
    path('lic-edit/<int:id>', license_views.edit, name='lic-edit'),
    path('lic-update/<int:id>', license_views.update, name='lic-update'),
    # path('lic-delete/<int:id>/<str:table>/', license_views.destroy, name='lic-delete'),
    path('lic-delete/<int:id>', license_views.destroy, name='lic-delete'),

    path('map/', common_views.Map.as_view(), name='map'),
    path('my-settings/', common_views.MySettings.as_view(), name='my_settings'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('create/', point_views.Create.as_view(), name='point_create'),
    path('edit/<int:pk>/', point_views.Edit.as_view(), name='point_edit'),
    path('delete/<int:pk>/', point_views.Delete.as_view(), name='point_delete'),
    path('info/<int:pk>/', point_views.AjaxInfo.as_view(), name='point_ajax_info'),
    path('detail/<int:pk>/', point_views.Detail.as_view(), name='point_detail'),
    path('ajax-points/', point_views.AjaxList.as_view(), name='point_ajax_list'),

    path('password-change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    path('password-recover/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-recover/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'cupp.point.views.custom_404_view'

admin.site.site_title = 'PP Management'
admin.site.site_header = 'PP Management'
admin.site.index_title = 'Administration'
