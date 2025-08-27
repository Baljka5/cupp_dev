from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse

from .forms import StrRentForm
from django.views import generic as g
from .models import StrRent
from django.shortcuts import render, redirect
from django.contrib import messages
from cupp.point.models import Point
from cupp.store_trainer.models import StoreTrainer


def rent_addnew(request):
    store_id_to_name = {rent.store_id: rent.store_name for rent in StoreTrainer.objects.all()}
    if request.method == "POST":
        form = StrRentForm(request.POST)
        if form.is_valid():
            store_id = request.POST.get('store_id')
            if store_id:
                try:
                    store_trainer_instance = StoreTrainer.objects.get(pk=store_id)
                    form.instance.store_id = store_trainer_instance
                except StoreTrainer.DoesNotExist:
                    messages.error(request, "Store ID is invalid.")
                    return render(request, 'rent/index.html', {'form': form, 'store_id_to_name': store_id_to_name})
            else:
                messages.error(request, "Store ID is missing.")
                return render(request, 'rent/index.html', {'form': form, 'store_id_to_name': store_id_to_name})
            try:
                form.instance.created_by = request.user if not form.instance.pk else form.instance.created_by
                form.instance.modified_by = request.user
                form.save()
                messages.success(request, "Event added successfully!")
                return redirect('/rent-index/')
            except Exception as e:
                messages.error(request, f"Error saving event: {e}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = StrRentForm()
    return render(request, 'rent/index.html', {'form': form, 'store_id_to_name': store_id_to_name})


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
    store_id_query = request.GET.get('store_id', '')
    str_name_query = request.GET.get('str_name', '')

    query = Q()
    if store_id_query.isdigit():
        query &= Q(store_id=store_id_query)
    elif store_id_query:
        query &= Q(store_id__name__icontains=store_id_query)

    if str_name_query:
        query &= Q(str_name__icontains=str_name_query)

    models = StrRent.objects.filter(query).distinct().order_by('id')
    paginator = Paginator(models, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "rent/show.html", {
        'page_obj': page_obj,
        'store_id_query': store_id_query,
        'str_name_query': str_name_query
    })


def edit(request, id):
    model = StrRent.objects.get(id=id)
    store_id_to_name = {rent.store_id: rent.store_name for rent in StoreTrainer.objects.all()}
    return render(request, 'rent/edit.html', {
        'model': model,
        'store_id_to_name': store_id_to_name})


# def update(request, id):
#     model = StrRent.objects.get(id=id)
#     form = StrRentForm(request.POST, instance=model)
#     if form.is_valid():
#         form.instance.modified_by = request.user
#         form.save()
#         return redirect("/rent-index/")
#     return render(request, 'rent/edit.html', {'model': model})

def update(request, id):
    model = StrRent.objects.get(id=id)
    form = StrRentForm(request.POST or None, instance=model)  # Include instance for pre-filling form with existing data
    if request.method == 'POST':
        if form.is_valid():
            form.instance.modified_by = request.user  # Ensure the modifier is the current user
            form.save()
            messages.success(request, 'Update successful.')
            return redirect('/rent-index/')  # Redirect to the appropriate URL after successful update
        else:
            messages.error(request, 'Error updating the form. Please check your data.')
    return render(request, 'rent/edit.html', {'form': form, 'model': model})


def destroy(request, id):
    model = StrRent.objects.get(id=id)
    model.delete()
    return redirect("/rent-index/")


def store_id_search(request):
    # Your logic to search for store ID based on query
    search_query = request.GET.get('q', '')
    if search_query:
        stores = StoreTrainer.objects.filter(name__icontains=search_query)
    else:
        stores = StoreTrainer.objects.none()

    store_list = [{'id': store.pk, 'text': store.name} for store in stores]
    return JsonResponse({'items': store_list})


class RentView(g.TemplateView):
    template_name = 'base.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the is_event_member variable
        context['is_event_member'] = self.request.user.groups.filter(name='Rent').exists()
        return context
