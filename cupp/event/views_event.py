from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse

from .forms import StoreDailyLogForm
from django.views import generic as g
from .models import StoreDailyLog, ActionCategory, ActionOwner, User
from django.shortcuts import render, redirect
from django.contrib import messages
from cupp.store_trainer.models import StoreTrainer
from cupp.point.models import Point


@login_required
def event_addnew(request):
    store_id_to_name = {event.store_id: event.store_name for event in StoreTrainer.objects.all()}
    action_categories = ActionCategory.objects.all()

    if request.user.groups.filter(name='license').exists():
        action_categories = action_categories.filter(activ_id__in=['A2', 'A4', 'A1'])

    if request.method == "POST":
        form = StoreDailyLogForm(request.POST)
        if form.is_valid():
            store_id = form.cleaned_data.get('store_no')
            print("Store No Received:", store_id)  # Debugging output
            if store_id:
                try:
                    store_trainer_instance = StoreTrainer.objects.get(store_id=store_id)
                    form.instance.store_id = store_trainer_instance
                except StoreTrainer.DoesNotExist:
                    messages.error(request, f"Store ID {store_id} is invalid.")
                    return render(request, 'event/event_index.html',
                                  {'form': form, 'store_id_to_name': store_id_to_name})
            else:
                messages.error(request, "Store ID is missing.")
                return render(request, 'event/event_index.html', {'form': form, 'store_id_to_name': store_id_to_name})
            form.instance.created_by = request.user if not form.instance.pk else form.instance.created_by
            form.instance.modified_by = request.user
            form.save()
            messages.success(request, "Event added successfully!")
            return redirect('/log-index/')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = StoreDailyLogForm()
        form.fields['activ_cat'].queryset = action_categories
    return render(request, 'event/event_index.html', {'form': form, 'store_id_to_name': store_id_to_name})


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
    activ_cat_query = request.GET.get('activ_cat', '')  # Get the search query parameter
    sort = request.GET.get('sort', 'id')  # Default sort is by 'id'
    order = request.GET.get('order', 'desc')  # Default order is ascending

    query = Q()
    if store_no_query:
        query &= Q(store_no__icontains=store_no_query)
    if activ_cat_query:
        query &= Q(activ_cat__activ_cat__icontains=activ_cat_query)

    if request.user.groups.filter(name='license').exists():
        license_users = User.objects.filter(groups__name='license')
        query &= Q(created_by__in=license_users)

    if sort:
        if order == 'asc':
            sort_field = sort
        else:  # Default or if 'desc'
            sort_field = f'-{sort}'
    else:
        sort_field = '-id'  # Default sorting if none specified

    models = StoreDailyLog.objects.filter(query).distinct().order_by(sort_field)

    paginator = Paginator(models, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "event/show.html",
                  {'page_obj': page_obj, 'store_no_query': store_no_query, 'activ_cat_query': activ_cat_query,
                   'sort': sort, 'order': order})


# def index(request):
#     models = StoreDailyLog.objects.all()
#     return render(request, "event/show.html", {'models': models})


def edit(request, id):
    model = StoreDailyLog.objects.get(id=id)
    categories = ActionCategory.objects.all()
    owners = ActionOwner.objects.all()
    store_id_to_name = {event.store_id: event.store_name for event in StoreTrainer.objects.all()}
    return render(request, 'event/edit.html',
                  {'model': model, 'categories': categories, 'owners': owners, 'store_id_to_name': store_id_to_name})


def update(request, id):
    model = StoreDailyLog.objects.get(id=id)
    form = StoreDailyLogForm(request.POST, instance=model)
    if request.method == 'POST':
        if form.is_valid():
            form.instance.modified_by = request.user
            form.save()
            messages.success(request, 'Update successful.')
            return redirect('/log-index/')
        else:
            messages.error(request, 'Error updating the form. Please check your data.')
    return render(request, 'event/edit.html', {'form': form, 'model': model})


def destroy(request, id):
    model = StoreDailyLog.objects.get(id=id)
    model.delete()
    return redirect("/log-index/")


def store_id_search(request):
    # Your logic to search for store ID based on query
    search_query = request.GET.get('q', '')
    if search_query:
        stores = StoreTrainer.objects.filter(name__icontains=search_query)
    else:
        stores = StoreTrainer.objects.none()

    store_list = [{'id': store.pk, 'text': store.name} for store in stores]
    return JsonResponse({'items': store_list})


class EventView(g.TemplateView):
    template_name = 'base.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the is_event_member variable
        context['is_event_member'] = self.request.user.groups.filter(name='Event').exists()
        return context
