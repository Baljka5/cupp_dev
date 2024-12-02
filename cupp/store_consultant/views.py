import json
import os
import datetime

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.db import transaction
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from cupp.store_consultant.models import Area, Consultants, Allocation, StoreConsultant, Tag, SC_Store_Allocation, \
    HisAllocation
from cupp.store_trainer.models import StoreTrainer
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from cupp.store_consultant.forms import StoreConsultantForm
from django.views import generic as g
from django.conf import settings
from django.templatetags.static import static


def index(request):
    store_id_query = request.GET.get('store_id', '')

    query = Q()
    if store_id_query:
        query &= Q(store_id__icontains=store_id_query)

    if request.user.groups.filter(name='SC Director').exists() or request.user.is_superuser:
        models = StoreConsultant.objects.all().order_by('id')
    else:
        models = StoreConsultant.objects.filter(query).distinct().order_by('id')

    if request.user.groups.filter(name='Store Consultant').exists():
        models = models.filter(sc_name__icontains=request.user.username)

    if request.user.groups.filter(name='Area').exists():
        models = models.filter(team_mgr__icontains=request.user.username)

    models = StoreConsultant.objects.filter(query)

    paginator = Paginator(models, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    team_mgr = "User"
    if request.user.is_authenticated:
        consultant = StoreConsultant.objects.filter(sc_name__icontains=request.user.username).first()
        if consultant:
            team_mgr = consultant.team_mgr if consultant.team_mgr else team_mgr

    return render(request, "store_consultant/show.html", {
        'page_obj': page_obj,
        'store_id_query': store_id_query,
        'user_name': request.user.username,
        'team_mgr': team_mgr
    })


def sc_view(request, id):
    try:
        model = StoreConsultant.objects.get(id=id)
        st_model = StoreTrainer.objects.get(id=id)
    except (StoreConsultant.DoesNotExist, StoreTrainer.DoesNotExist):
        raise Http404("Store not found")

    # Define paths for JPG, PNG, and JPEG images in the static directory
    jpg_image_path = os.path.join(settings.STATIC_ROOT, 'store', f'{model.store_id}.jpg')
    png_image_path = os.path.join(settings.STATIC_ROOT, 'store', f'{model.store_id}.png')
    jpeg_image_path = os.path.join(settings.STATIC_ROOT, 'store', f'{model.store_id}.jpeg')

    # Check if any of the image files exist
    if os.path.exists(jpg_image_path):
        store_image = f'store/{model.store_id}.jpg'
    elif os.path.exists(png_image_path):
        store_image = f'store/{model.store_id}.png'
    elif os.path.exists(jpeg_image_path):
        store_image = f'store/{model.store_id}.jpeg'
    else:
        store_image = None

    return render(request, 'store_consultant/sc_index.html', {
        'model': model,
        'st_model': st_model,
        'store_image': store_image,
    })


def store_view(request, id):
    try:
        store = StoreConsultant.objects.get(id=id)  # Use `id` to query the store
    except StoreConsultant.DoesNotExist:
        raise Http404("Store not found")

    store_name = store.store_name

    jpg_image_path = os.path.join(settings.STATIC_ROOT, 'images', 'stores', f'{store.store_id}.jpg')
    png_image_path = os.path.join(settings.STATIC_ROOT, 'images', 'stores', f'{store.store_id}.png')

    if os.path.exists(jpg_image_path):
        store_image = static(f'images/stores/{store.store_id}.jpg')
    elif os.path.exists(png_image_path):
        store_image = static(f'images/stores/{store.store_id}.png')
    else:
        store_image = None

    return render(request, 'store_consultant/sc_index.html', {
        'store_image': store_image,
        'store_id': store.store_id,
        'store_name': store_name,
    })


def edit(request, id):
    model = StoreConsultant.objects.get(id=id)
    return render(request, 'store_consultant/edit.html', {'model': model})


def update(request, id):
    model = StoreConsultant.objects.get(id=id)
    form = StoreConsultantForm(request.POST, instance=model)
    if form.is_valid():
        form.save()
        return redirect("/store-index")
    return render(request, 'store_consultant/edit.html', {'model': model})


# def update(request, id):
#     model = get_object_or_404(StoreConsultant, id=id)
#
#     if request.method == 'POST':
#         print(request.POST)
#         form = StoreConsultantForm(request.POST, instance=model)
#         if form.is_valid():
#             form.save()  # Save updated data to the database
#             return redirect("/store-index")
#         else:
#             print(form.errors)  # Log form errors for debugging
#     else:
#         form = StoreConsultantForm(instance=model)
#
#     return render(request, 'store_consultant/edit.html', {'form': form, 'model': model})


def scIndex(request):
    current_date = datetime.datetime.now()
    current_year = current_date.year
    current_month = current_date.month

    # Only show current year and the next two years
    next_three_years = [current_year + i for i in range(3)]

    # Define months
    months = [
        {'value': 'JAN', 'name': 'January'},
        {'value': 'FEB', 'name': 'February'},
        {'value': 'MAR', 'name': 'March'},
        {'value': 'APR', 'name': 'April'},
        {'value': 'MAY', 'name': 'May'},
        {'value': 'JUN', 'name': 'June'},
        {'value': 'JUL', 'name': 'July'},
        {'value': 'AUG', 'name': 'August'},
        {'value': 'SEP', 'name': 'September'},
        {'value': 'OCT', 'name': 'October'},
        {'value': 'NOV', 'name': 'November'},
        {'value': 'DEC', 'name': 'December'},
    ]

    # Filter months to only show current and future months of the year
    remaining_months = [month for month in months if months.index(month) + 1 >= current_month]

    # Fetch the last saved allocation's year and month
    last_allocation = Allocation.objects.order_by('-created_date').first()
    last_year = last_allocation.year if last_allocation else current_year
    last_month = last_allocation.month if last_allocation else 'jan'

    # Fetch areas, consultants, and store consultants
    areas = Area.objects.all()
    consultants = Consultants.objects.annotate(
        store_count=Count('store_allocations')  # Corrected related name
    )
    store_consultants = StoreConsultant.objects.all()

    context = {
        'areas': areas,
        'consultants': consultants,
        'store_consultants': store_consultants,
        'next_three_years': next_three_years,  # Pass filtered years
        'months': remaining_months,  # Pass filtered months
        'last_year': last_year,  # Pass the last saved year to the template
        'last_month': last_month,  # Pass the last saved month to the template
    }

    return render(request, 'store_consultant/index.html', context)


def get_team_data(request, team_id):
    # Assuming team_id is passed correctly and you have a model Consultants with a related field allocation
    scs = Consultants.objects.filter(allocation__area_id=team_id).values('id', 'sc_name')
    team_scs = list(scs)
    # Assuming you need to pass store allocations or other details, add them here
    return JsonResponse({'team_scs': team_scs})


@csrf_protect
@require_POST
def update_consultant_area(request):
    consultant_id = request.POST.get('consultantId')
    target_area_id = request.POST.get('targetAreaId')

    try:
        consultant = Consultants.objects.get(id=consultant_id)

        if target_area_id == 'not-allocated':
            # Assuming that a null foreign key on consultant represents not-allocated
            consultant.area = None
        else:
            # Assuming that the area_id is a ForeignKey in Consultants model
            consultant.area = Area.objects.get(id=target_area_id)

        consultant.save()
        return JsonResponse({'status': 'success'})
    except (Consultants.DoesNotExist, Area.DoesNotExist) as e:
        return JsonResponse({'status': 'failed', 'message': str(e)}, status=400)


@require_POST
def update_consultant_store(request):
    consultant_id = request.POST.get('consultantId')
    target_area_id = request.POST.get('targetAreaId')

    try:
        consultant = Consultants.objects.get(id=consultant_id)

        if target_area_id == 'not-allocated':
            consultant.area = None
        else:
            consultant.area = Area.objects.get(id=target_area_id)
        consultant.save()
        return JsonResponse({'status': 'success'})
    except (Consultants.DoesNotExist, Area.DoesNotExist) as e:
        return JsonResponse({'status': 'failed', 'message': str(e)}, status=400)


def get_unallocated_stores(request):
    unallocated_stores = StoreConsultant.objects.filter(
        ~Q(store_id__in=SC_Store_Allocation.objects.values_list('store__store_id', flat=True)))
    store_data = [{'store_id': store.store_id, 'store_name': store.store_name} for store in unallocated_stores]
    return JsonResponse({'stores': store_data})


@csrf_protect
@require_POST
def save_allocations(request):
    try:
        # Parse the incoming data from the request body
        data = json.loads(request.body)
        allocations = data.get('allocations', [])
        year = data.get('year')
        month = data.get('month')

        # Debugging: Log the incoming allocations data
        print("Received allocations:", allocations)

        with transaction.atomic():
            for allocation in allocations:
                consultant_id = allocation.get('consultantId')
                area_id = allocation.get('areaId')

                # Fetch the consultant object
                consultant = Consultants.objects.get(id=consultant_id)

                # Fetch the area, set to None if 'not-allocated'
                area = Area.objects.get(id=area_id) if area_id != 'not-allocated' else None

                # Delete existing allocations for the consultant to avoid duplicates
                Allocation.objects.filter(consultant=consultant).delete()

                # Create a new allocation
                Allocation.objects.create(
                    consultant=consultant,
                    area=area,
                    year=year,
                    month=month
                )

        return JsonResponse({'status': 'success'})

    except Consultants.DoesNotExist:
        return JsonResponse({'status': 'failed', 'message': 'Consultant does not exist'}, status=400)

    except Area.DoesNotExist:
        return JsonResponse({'status': 'failed', 'message': 'Area does not exist'}, status=400)

    except Exception as e:
        # Log the full error details for easier debugging
        print(f"Error during save_allocations: {str(e)}")
        return JsonResponse({'status': 'failed', 'message': str(e)}, status=500)


@csrf_protect
@require_POST
def save_consultant_stores(request):
    try:
        data = json.loads(request.body)
        store_allocations = data.get('storeAllocations', [])
        results = []
        reassignment_warnings = []

        with transaction.atomic():
            for store_allocation in store_allocations:
                consultant_id = store_allocation.get('consultantId')
                store_nos = store_allocation.get('storeIds', [])

                # Fetch the consultant object
                consultant = Consultants.objects.get(id=consultant_id)
                sc_name = consultant.sc_name

                for store_no in store_nos:
                    store = StoreConsultant.objects.get(store_id=store_no)

                    # Check if the store is already allocated
                    existing_allocation = SC_Store_Allocation.objects.filter(store=store).first()
                    if existing_allocation and existing_allocation.consultant.id != consultant_id:
                        # Add warning if reassignment occurs
                        reassignment_warnings.append({
                            'store_id': store.store_id,
                            'previous_sc_name': existing_allocation.consultant.sc_name,
                            'new_sc_name': sc_name
                        })

                    # Remove the store from its current allocation if necessary
                    SC_Store_Allocation.objects.filter(store=store).delete()

                    # Assign the store to the new consultant
                    SC_Store_Allocation.objects.create(
                        consultant=consultant,
                        store=store,
                        store_name=store.store_name,
                        sc_name=sc_name,
                        store_no=store.store_id
                    )

                results.append({
                    'status': 'success',
                    'consultant_id': consultant_id,
                    'sc_name': sc_name,
                    'store_ids': store_nos
                })

        return JsonResponse({'results': results, 'reassignment_warnings': reassignment_warnings})

    except StoreConsultant.DoesNotExist as e:
        return JsonResponse({'status': 'failed', 'message': f'Store not found: {str(e)}'}, status=400)
    except Consultants.DoesNotExist as e:
        return JsonResponse({'status': 'failed', 'message': f'Consultant not found: {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'failed', 'message': str(e)}, status=500)


def get_allocations(request):
    allocations = Allocation.objects.all().values('id', 'consultant__id', 'area__id', 'year', 'month')
    return JsonResponse(list(allocations), safe=False)


class StoreConsultantView(g.TemplateView):
    template_name = 'base.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the is_event_member variable
        context['is_event_member'] = self.request.user.groups.filter(name='Store Consultant').exists()
        return context


class AreaView(g.TemplateView):
    template_name = 'base.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['is_event_member'] = self.request.user.groups.filter(name='Area').exists()
        return context


class SCDirectorView(g.TemplateView):
    template_name = 'base.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['is_event_member'] = self.request.user.groups.filter(name='SC Director').exists()
        return context


def get_scs_by_team(request, team_id):
    scs = Consultants.objects.filter(allocation__area_id=team_id)
    sc_data = []

    # Get a list of already allocated stores (across all consultants)
    allocated_stores = SC_Store_Allocation.objects.values_list('store__store_id', flat=True).distinct()

    for sc in scs:
        # Get the store IDs and names allocated to the consultant
        store_allocations = SC_Store_Allocation.objects.filter(consultant=sc)
        store_ids = list(store_allocations.values_list('store__store_id', flat=True))  # Get store IDs
        store_names = list(store_allocations.values_list('store_name', flat=True))  # Get store names

        sc_data.append({
            "id": sc.id,
            "name": sc.sc_name,
            "store_ids": store_ids,  # Send store IDs to frontend
            "store_names": store_names  # Send store names to frontend
        })

    return JsonResponse({'scs': sc_data, 'allocated_stores': list(allocated_stores)})


def assign_stores(request):
    if request.method == 'POST':
        store_ids = request.POST.getlist('store_ids')
        consultant_id = request.POST.get('consultant_id')
        consultant = Consultants.objects.get(id=consultant_id)

        # Clear previous stores assignments
        consultant.stores.clear()

        # Add new stores based on selected options
        consultant.stores.add(*store_ids)
        return redirect('some-view-name')
    else:
        stores = StoreConsultant.objects.all()
        return render(request, 'assign_stores.html', {'stores': stores})


def populate_historical_allocations():
    for allocation in Allocation.objects.all():
        sc_store_allocations = SC_Store_Allocation.objects.filter(consultant=allocation.consultant)

        for sc_store_allocation in sc_store_allocations:
            HisAllocation.objects.create(
                consultant=allocation.consultant,
                store=sc_store_allocation.store,
                store_name=sc_store_allocation.store_name,
                sc_name=sc_store_allocation.sc_name,
                store_no=sc_store_allocation.store_no,
                year=allocation.year,
                month=allocation.month,
                team_no=allocation.team_no,
                area=allocation.area,
                store_cons=allocation.store_cons,
                tags=allocation.tags
            )
    print("Historical data populated successfully!")


# Run the script
populate_historical_allocations()

# def get_unallocated_stores(request):
#     unallocated_stores = StoreConsultant.objects.filter(allocation__isnull=True)
#     store_data = [{'store_id': store.store_id} for store in unallocated_stores]
#     return JsonResponse({'stores': store_data})
