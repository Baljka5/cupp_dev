from datetime import datetime, timedelta

from django.views import generic as g
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from .forms import PointForm, PhotoFormset, StorePlanningForm
from .models import Point, District, City, Type, StorePlanning
from .mixins import GroupMixin, StorePlannerMixin
from django.contrib.auth.models import Group, User
from django import template


# from cupp.store_planning.models import StorePlanning


def custom_404_view(request, exception):
    return render(request, '404.html', status=404)


class FormBase(GroupMixin):
    model = Point
    # st_model = StorePlanning
    template_name = 'point/form.html'
    form_class = PointForm

    success_url = reverse_lazy('map')

    def form_valid(self, form):
        context = self.get_context_data()
        photo_formset = context['photo_formset']
        if photo_formset.is_valid():
            form.instance.created_by = self.request.user if not form.instance.pk else form.instance.created_by
            form.instance.modified_by = self.request.user
            instance = form.save()

            photo_formset.instance = instance
            photo_formset.save()

            if form.data.get('next'):
                return redirect('/create/')

            return super(FormBase, self).form_valid(form)

        context['photo_formset'] = photo_formset
        context['form'] = form
        return self.render_to_response(context)


class Create(LoginRequiredMixin, FormBase, g.CreateView):

    def get_form_kwargs(self):
        kwargs = super(Create, self).get_form_kwargs()
        kwargs['user'] = self.request.user  # Add the user to form kwargs
        return kwargs

    def get_context_data(self, *args, **kwargs):
        context = super(Create, self).get_context_data(*args, **kwargs)
        if self.request.method == 'GET':
            context['photo_formset'] = PhotoFormset()
            context['store_planning_form'] = StorePlanningForm()
        else:
            context['photo_formset'] = PhotoFormset(self.request.POST, self.request.FILES)
            context['store_planning_form'] = StorePlanningForm(self.request.POST)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        photo_formset = context['photo_formset']
        store_planning_form = context['store_planning_form']

        if photo_formset.is_valid() and store_planning_form.is_valid():
            # This saves the Point instance
            form.instance.created_by = self.request.user
            self.object = form.save()

            # Now, save the StorePlanning instance
            store_planning = store_planning_form.save(commit=False)
            store_planning.point = self.object  # Link the StorePlanning instance to the Point instance
            store_planning.save()

            # Save the photos
            photo_formset.instance = self.object
            photo_formset.save()

            return redirect(self.get_success_url())

        # If forms are not valid, return to the form with errors
        return self.render_to_response(
            self.get_context_data(form=form, photo_formset=photo_formset, store_planning_form=store_planning_form))
    # def form_valid(self, form):
    #     response = super(Create, self).form_valid(form)  # This saves the Point instance
    #     point_instance = form.instance
    #
    #     # Now, create or update StorePlanning instance
    #     store_planning_defaults = {
    #         'store_name': point_instance.store_name,
    #         'lat': point_instance.lat,
    #         'lon': point_instance.lon,
    #         # Add all fields you want to copy
    #     }
    #     StorePlanning.objects.update_or_create(
    #         store_id=point_instance.store_id,
    #         defaults=store_planning_defaults
    #     )
    #
    #     return response


class Edit(FormBase, StorePlannerMixin, g.UpdateView):

    def get_form_kwargs(self):
        kwargs = super(Edit, self).get_form_kwargs()
        kwargs['user'] = self.request.user  # Add the user to form kwargs
        return kwargs

    def get_context_data(self, *args, **kwargs):
        context = super(Edit, self).get_context_data(*args, **kwargs)
        if self.request.method == 'GET':
            context['photo_formset'] = PhotoFormset(instance=self.object)
            context['store_planning_form'] = StorePlanningForm(instance=self.object)
        else:
            context['photo_formset'] = PhotoFormset(self.request.POST, files=self.request.FILES, instance=self.object)
            context['store_planning_form'] = StorePlanningForm(self.request.POST, instance=self.object)

        return context


class Delete(GroupMixin, StorePlannerMixin, g.DeleteView):
    model = Point
    success_url = reverse_lazy('map')


class AjaxInfo(GroupMixin, StorePlannerMixin, g.DetailView):
    model = Point
    template_name = 'point/ajax_info.html'


class Detail(LoginRequiredMixin, g.DetailView):
    model = Point
    template_name = 'point/detail.html'


def sp_data(request, point):
    model = StorePlanning.objects.get(point=point)
    print(model)
    return render(request, 'point/detail.html', {'model': model})


class AjaxList(LoginRequiredMixin, g.ListView):
    model = Point
    template_name = 'point/ajax_list.html'

    def get_queryset(self):
        types = self.request.GET.getlist('type')
        user = self.request.user
        grades = self.request.GET.getlist('grade')
        availables = self.request.GET.getlist('availability')
        size = self.request.GET.get('size')
        base_rent_rate = self.request.GET.get('base_rent_rate')
        max_rent_rate = self.request.GET.get('max_rent_rate')
        available_date = self.request.GET.get('available_date')
        created_by = self.request.GET.get('created_by')
        created_date = self.request.GET.get('created_date')

        kwargs = {
            'type': 'PP'
        }

        if grades:
            kwargs['grade__in'] = grades

        if availables:
            kwargs['availability__in'] = [int(i) for i in availables if i.isdigit()]

        if size and size != '0;300':
            sgte, slte = size.split(';')
            kwargs['size__gte'] = sgte
            kwargs['size__lte'] = slte

        if base_rent_rate and base_rent_rate != '0;20000000':
            bgte, blte = base_rent_rate.split(';')
            kwargs['base_rent_rate__gte'] = bgte
            kwargs['base_rent_rate__lte'] = blte

        if max_rent_rate and max_rent_rate != '0;20000000':
            mgte, mlte = max_rent_rate.split(';')
            kwargs['max_rent_rate__gte'] = mgte
            kwargs['max_rent_rate__lte'] = mlte

        if available_date:
            range_value = available_date.replace('/', '-').split(' - ')
            kwargs['available_date__gte'] = datetime.strptime(range_value[0], '%Y-%m-%d')
            kwargs['available_date__lte'] = datetime.strptime(range_value[1], '%Y-%m-%d') + timedelta(days=1)

        if created_date:
            range_value = created_date.replace('/', '-').split(' - ')
            kwargs['created_date__gte'] = datetime.strptime(range_value[0], '%Y-%m-%d')
            kwargs['created_date__lte'] = datetime.strptime(range_value[1], '%Y-%m-%d') + timedelta(days=1)

        if created_by:
            kwargs['created_by__id'] = created_by

        if user.is_superuser:
            return Point.objects.all()

        qs = Point.objects.none()

        if user.groups.filter(name='Manager').exists() or user.is_superuser or user.groups.filter(
                name='SP Director').exists():
            pp_qs = Point.objects.filter(type='PP')  # Get all PP types for Managers and superusers
            qs = qs.union(pp_qs)

        if user.groups.filter(name='Store planner').exists() or user.is_superuser:
            pp_qs = Point.objects.filter(created_by=user, type='PP')
            qs = qs.union(pp_qs)

            # For other types, if selected, include them in the queryset but exclude PP type points created by other users.
        if types:
            non_pp_qs = Point.objects.filter(type__in=types).exclude(type='PP')
            qs = qs.union(non_pp_qs)
        # if types:
        #     qs = Point.objects.filter(Q(**kwargs) | Q(type__in=types))
        # else:
        #     qs = Point.objects.filter(**kwargs)
        #
        # user = self.request.user
        # if user.groups.filter(name='Store planner').exists():
        #     qs = qs.filter(Q(created_by=user, type='PP') | Q(type__in=types))

        return qs


def get_districts(request):
    city_id = request.GET.get('city_id')
    districts = list(District.objects.filter(city__id=city_id).values('id', 'district_name'))
    return JsonResponse({'districts': districts})


def display_groups(request):
    users = User.objects.prefetch_related('groups').all()
    return render(request, 'point/test.html', {'users': users})


def bi_embed(request):
    users = User.objects.prefetch_related('groups').all()
    return render(request, 'point/test1.html', {'users': users})


# def get_type_name(request):
#     type_code = request.GET.get('type_code', '')
#     try:
#         type_obj = Type.objects.get(type_cd=type_code)
#         return JsonResponse({'type_name': type_obj.type_name})
#     except Type.DoesNotExist:
#         return JsonResponse({'type_name': 'Not found'})

def index(request):
    is_event_user = request.user.groups.filter(name='Event').exists() or request.user.is_superuser
    return render(request, 'base.html', {'user': request.user, 'is_event_user': is_event_user})


@login_required
def custom_login_redirect(request):
    if request.user.is_superuser:
        return redirect('/map/')
    elif request.user.groups.filter(name='Event').exists():
        return redirect('/log-index/')
    elif request.user.groups.filter(name='license').exists():
        return redirect('/register-license/')
    elif request.user.groups.filter(name='legal_team').exists():
        return redirect('/register-license/')
    elif request.user.groups.filter(name='Store planner').exists():
        return redirect('/map/')
    elif request.user.groups.filter(name='Manager').exists():
        return redirect('/map/')
    elif request.user.groups.filter(name='SP Director').exists():
        return redirect('/map/')
    elif request.user.groups.filter(name='Rent').exists():
        return redirect('/rent-index/')
    elif request.user.groups.filter(name='Store Trainer').exists():
        return redirect('/st-index/')
    elif request.user.groups.filter(name='Store Consultant').exists():
        return redirect('/store-index/')
    elif request.user.groups.filter(name='Area').exists():
        return redirect('/store-index/')
    elif request.user.groups.filter(name='SC Director').exists():
        return redirect('/store-index/')
    elif request.user.groups.filter(name='ST Manager').exists():
        return redirect('/st-index/')
    elif request.user.groups.filter(name='planning_manager').exists():
        return redirect('/sc-index/')
    else:
        return redirect('/default-redirect/')
