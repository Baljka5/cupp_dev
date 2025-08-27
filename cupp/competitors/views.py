from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse

from .forms import StoreCompetitorsForm
from django.views import generic as g
from .models import StoreCompetitors, DimCluster, DimCompType
from django.shortcuts import render, redirect
from django.contrib import messages
from cupp.store_trainer.models import StoreTrainer
from cupp.point.models import Point


@login_required
def comp_addnew(request):
    store_id_to_name = {competitor.store_id: competitor.store_name for competitor in StoreTrainer.objects.all()}
    if request.method == "POST":
        form = StoreCompetitorsForm(request.POST)
        if form.is_valid():
            # Handle schedule type logic
            schedule_type = form.cleaned_data.get('comp_schedule_tp')
            if schedule_type == '24H':
                form.instance.comp_schedule_time = '00:00-23:59'
            elif schedule_type == '17H':
                form.instance.comp_schedule_time = '07:00-00:00'

            # Handle store ID assignment
            store_id = request.POST.get('store_no')
            if store_id:
                try:
                    store_trainer_instance = StoreTrainer.objects.get(pk=store_id)
                    form.instance.store_id = store_trainer_instance.store_id
                except StoreTrainer.DoesNotExist:
                    messages.error(request, f"Store ID {store_id} is invalid.")
                    return render(request, 'competitors/index.html',
                                  {'form': form, 'store_id_to_name': store_id_to_name})
            else:
                messages.error(request, "Store ID is missing.")
                return render(request, 'competitors/index.html', {'form': form, 'store_id_to_name': store_id_to_name})

            # Attempt to save form
            try:
                form.instance.created_by = request.user
                form.instance.modified_by = request.user
                form.save()
                messages.success(request, "Event added successfully!")
                return redirect('/comp-index/')
            except Exception as e:
                messages.error(request, f"Error saving event: {e}")

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = StoreCompetitorsForm()
    return render(request, 'competitors/index.html', {'form': form, 'store_id_to_name': store_id_to_name})


# def event_addnew(request):
#     # model = MainTable
#     # form_class = MainTableForm
#     # template_name = 'license/show.html'
#     # success_url = reverse_lazy('map')
#     if request.method == "POST":
#         form = StoreDailyLogForm(request.POST)
#         if form.is_valid():
#             try:
#                 form.save()
#                 return redirect('/')
#             except:
#                 pass
#     else:
#         form = StoreDailyLogForm()
#     return render(request, 'event/event_index.html', {'form': form})


def index(request):
    store_no_query = request.GET.get('store_no', '')
    activ_cat_query = request.GET.get('comp_name', '')  # Get the search query parameter
    sort = request.GET.get('sort', 'id')  # Default sort is by 'id'
    order = request.GET.get('order', 'desc')  # Default order is ascending

    query = Q()
    if store_no_query:
        query &= Q(store_id__icontains=store_no_query)
    if activ_cat_query:
        query &= Q(comp_name__comp_name__icontains=activ_cat_query)

    if sort:
        if order == 'asc':
            sort_field = sort
        else:  # Default or if 'desc'
            sort_field = f'-{sort}'
    else:
        sort_field = '-id'  # Default sorting if none specified

    models = StoreCompetitors.objects.filter(query).distinct().order_by(sort_field)

    paginator = Paginator(models, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "competitors/show.html",
                  {'page_obj': page_obj, 'store_no_query': store_no_query, 'activ_cat_query': activ_cat_query})


# def index(request):
#     models = StoreDailyLog.objects.all()
#     return render(request, "event/show.html", {'models': models})


def edit(request, id):
    model = StoreCompetitors.objects.get(id=id)
    dim_clusters = DimCluster.objects.all()
    dim_types = DimCompType.objects.all()
    store_id_to_name = {competitor.store_id: competitor.store_name for competitor in StoreTrainer.objects.all()}
    return render(request, 'competitors/edit.html', {
        'model': model,
        'dim_clusters': dim_clusters,
        'dim_types': dim_types,
        'store_id_to_name': store_id_to_name
    })


@login_required
def update(request, id):
    model = StoreCompetitors.objects.get(id=id)
    form = StoreCompetitorsForm(request.POST, instance=model)
    if request.method == 'POST':
        if form.is_valid():
            # Handle schedule type logic
            schedule_type = form.cleaned_data.get('comp_schedule_tp')
            if schedule_type == '24H':
                form.instance.comp_schedule_time = '00:00-23:59'
            elif schedule_type == '17H':
                form.instance.comp_schedule_time = '07:00-00:00'

            # Attempt to save form
            try:
                form.instance.modified_by = request.user
                form.save()
                messages.success(request, 'Update successful.')
                return redirect('/comp-index/')
            except Exception as e:
                messages.error(request, f"Error updating the form: {e}")

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    return render(request, 'competitors/edit.html', {'form': form, 'model': model})


def destroy(request, id):
    model = StoreCompetitors.objects.get(id=id)
    model.delete()
    return redirect("/comp-index/")


def store_id_search(request):
    search_query = request.GET.get('q', '')
    if search_query:
        stores = StoreTrainer.objects.filter(name__icontains=search_query)
    else:
        stores = StoreTrainer.objects.none()

    store_list = [{'id': store.pk, 'text': store.name} for store in stores]
    return JsonResponse({'items': store_list})


class CompView(g.TemplateView):
    template_name = 'base.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the is_event_member variable
        context['is_event_member'] = self.request.user.groups.filter(name='Store Consultant').exists()
        return context
