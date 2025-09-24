from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from cupp.store_consultant import views as sc_views
from cupp.competitors import views as comp_views
from cupp.event import views_event as event_views
from cupp.license import views_lic as license_views
from cupp.rent import views_rent as rent_views
from cupp.dispute import views as leg_views
 
urlpatterns = [
    path('', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
 
    path('lock-list/', sc_views.lock_list, name='lock-list'),
    path('lock-update/', sc_views.lock_update, name='lock-update'),
    path('get-unallocated-stores/', sc_views.get_unallocated_stores, name='get_unallocated_stores'),
 
    path('sc-index/', sc_views.scIndex, name='sc-index'),
    path('store-index/', sc_views.index, name='store-index'),
    path('sc-view/<int:id>', sc_views.sc_view, name='sc-views'),
    path('sc-edit/<int:id>', sc_views.edit, name='sc-edit'),
    path('sc-update/<int:id>', sc_views.update, name='sc-update'),
    path('update_consultant_area/', sc_views.update_consultant_area, name='update_consultant_area'),
 
    path('save-allocations/', sc_views.save_allocations, name='save_allocations'),
    path('get-allocations/', sc_views.get_allocations, name='get_allocations'),
    path('get-team-data/<int:team_id>/', sc_views.get_team_data, name='get_team_data'),
    path('get-scs-by-team/<int:team_id>/', sc_views.get_scs_by_team, name='get_scs_by_team'),
    path('clear-allocations/', sc_views.clear_allocations, name='clear_allocations'),
    path('push-data/', sc_views.push_data, name='push_data'),
    path('search-store-allocation/', sc_views.search_store_allocation, name='search_store_allocation'),
 
    path('sc-add-index/', sc_views.sc_add_index, name='sc-add-index'),
    path('save-consultant-stores/', sc_views.save_consultant_stores, name='save-consultant-stores'),
 
    path('admin/', admin.site.urls),

    path('comp-index/', comp_views.index, name='comp_index'),
    path('comp-create', comp_views.comp_addnew, name='comp-create'),
    path('comp-edit/<int:id>', comp_views.edit, name='comp-edit'),
    path('comp-update/<int:id>', comp_views.update, name='comp_update'),
    path('comp-delete/<int:id>', comp_views.destroy, name='comp-delete'),

    path('log-index/', event_views.index, name='event_index'),
    path('log-create', event_views.event_addnew, name='event-create'),
    path('log-edit/<int:id>', event_views.edit, name='event-edit'),
    path('log-update/<int:id>', event_views.update, name='event_update'),
    path('log-delete/<int:id>', event_views.destroy, name='log-delete'),

    path('register-license/', license_views.index, name='index'),
    path('addnew', license_views.addnew, name='addnew'),
    path('lic-edit/<int:id>', license_views.edit, name='lic-edit'),
    path('lic-update/<int:id>', license_views.update, name='lic-update'),
    # path('lic-delete/<int:id>/<str:table>/', license_views.destroy, name='lic-delete'),
    path('lic-delete/<int:id>', license_views.destroy, name='lic-delete'),

    path('rent-index/', rent_views.index, name='rent_index'),
    path('rent-create', rent_views.rent_addnew, name='rent-create'),
    path('rent-edit/<int:id>', rent_views.edit, name='rent-edit'),
    path('rent-update/<int:id>', rent_views.update, name='rent-update'),
    path('rent-delete/<int:id>', rent_views.destroy, name='rent-delete'),
    path('api/store-id-search/', rent_views.store_id_search, name='store_id_search'),

    path('leg-index/', leg_views.index, name='leg-index'),
    path('leg-add', leg_views.leg_add, name='leg-add'),
    path('leg-edit/<int:id>', leg_views.edit, name='leg-edit'),
    path('leg-update/<int:id>', leg_views.update, name='leg-update'),
    path('leg-delete/<int:id>', leg_views.destroy, name='leg-delete'),
]
 
admin.site.site_title = 'Store Management'
admin.site.site_header = 'Store Consultant Management'
admin.site.index_title = 'SC Administration'