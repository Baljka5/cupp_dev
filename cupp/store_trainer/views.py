from django.shortcuts import render

# Create your views here.
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse

from .forms import StoreTrainerForm
from .models import StoreTrainer
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import generic as g


# def st_addnew(request):
#     # lic_id_to_name = {dimension.lic_id: dimension.lic_id_nm for dimension in DimensionTable.objects.all()}
#     if request.method == "POST":
#         form = StoreTrainer(request.POST)
#         if form.is_valid():
#             try:
#
#                 form.save()
#                 messages.success(request, 'Form submission successful.')
#                 return redirect('/st-create')
#             except Exception as e:
#                 # If save fails, add an error message and print the exception
#                 messages.error(request, 'Form could not be saved. Please try again.')
#                 print(f"Error saving form: {e}")
#     else:
#         form = StoreTrainerForm()
#     return render(request, 'store_trainer/index.html', {
#         'form': form,
#     })


# def index(request):
#     models = MainTable.objects.all()
#     return render(request, "license/show.html", {'models': models})

def index(request):
    store_id_query = request.GET.get('store_id', '')
    lic_id_nm_query = request.GET.get('lic_id_nm', '')

    query = Q()
    if store_id_query:
        query &= Q(store_id__icontains=store_id_query)
    if lic_id_nm_query:
        query &= Q(lic_id__lic_id_nm__icontains=lic_id_nm_query)

    if request.user.groups.filter(name='ST Manager').exists() or request.user.is_superuser:
        models = StoreTrainer.objects.all().order_by('id')
    else:
        models = StoreTrainer.objects.filter(query).distinct().order_by('id')

    # Filtering for users in the "Store Consultant" group
    if request.user.groups.filter(name='Store Trainer').exists():
        if request.user.is_authenticated:
            user_first_name = request.user.first_name
            models = models.filter(st_name__icontains=user_first_name)

    # Additional filtering for users in the "Area" group

    paginator = Paginator(models, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "store_trainer/show.html", {
        'page_obj': page_obj,
        'store_id_query': store_id_query,
        'lic_id_nm_query': lic_id_nm_query,
        'user_name': request.user.username,
    })


def edit(request, id):
    model = StoreTrainer.objects.get(id=id)
    form = StoreTrainerForm(instance=model)
    return render(request, 'store_trainer/edit.html', {'model': model, 'form': form})


def update(request, id):
    model = StoreTrainer.objects.get(id=id)
    form = StoreTrainerForm(request.POST, instance=model)
    if form.is_valid():
        form.save()
        return redirect("/st-index/")
    return render(request, 'store_trainer/edit.html', {'model': model, 'form': form})


def st_view(request, id):
    model = StoreTrainer.objects.get(id=id)
    return render(request, 'store_trainer/index.html', {'model': model})


def update(request, id):
    model = StoreTrainer.objects.get(id=id)
    form = StoreTrainerForm(request.POST, instance=model)
    if form.is_valid():
        form.save()
        return redirect("/st-index/")
    return render(request, 'store_trainer/edit.html', {'model': model, 'form': form})


# def update(request, id):
#     model = StoreTrainer.objects.get(id=id)
#     if request.method == 'POST':
#         form = StoreTrainerForm(request.POST, instance=model)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Store Trainer updated successfully.')
#             return redirect('/st-index')
#         else:
#             # If form is not valid, print the errors to the console
#             print(form.errors)
#             messages.error(request, 'Error updating the Store Trainer. Please check the form for errors.')
#     else:
#         form = StoreTrainerForm(instance=model)
#
#     return render(request, 'store_trainer/edit.html', {'form': form, 'model': model})


#
#
# def destroy(request, id):
#     model = MainTable.objects.get(id=id)
#     model.delete()
#     return redirect("/register-license")

class StoreTrainerView(g.TemplateView):
    template_name = 'base.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the is_event_member variable
        context['is_event_member'] = self.request.user.groups.filter(name='Store Trainer').exists()
        return context


class StoreTrainerManagerView(g.TemplateView):
    template_name = 'base.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the is_event_member variable
        context['is_event_member'] = self.request.user.groups.filter(name='ST Manager').exists()
        return context
