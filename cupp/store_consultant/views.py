import json
import os
import datetime
from django.views.decorators.http import require_GET

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.db import transaction
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from cupp.store_consultant.models import Area, Consultants, Allocation, StoreConsultant, Tag, SC_Store_Allocation, \
    HisAllocation, AllocationTemp, SC_Store_AllocationTemp
from cupp.store_trainer.models import StoreTrainer
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from cupp.store_consultant.forms import StoreConsultantForm
from django.views import generic as g
from django.conf import settings
from django.templatetags.static import static
from django.contrib import messages


@login_required
def index(request):
    store_id_query = request.GET.get('store_id', '')

    query = Q()
    if store_id_query:
        query &= Q(store_id__icontains=store_id_query)

    # Fetch all stores for SC Director or Superuser
    if request.user.groups.filter(name='SC Director').exists() or request.user.is_superuser:
        models = StoreConsultant.objects.filter(query).order_by('id')

    # Fetch stores assigned to the logged-in Store Consultant
    elif request.user.groups.filter(name='Store Consultant').exists():
        models = StoreConsultant.objects.filter(
            query & Q(sc_name__icontains=request.user.username)).distinct().order_by('id')

    # Fetch stores assigned to the logged-in Area Manager
    elif request.user.groups.filter(name='Area').exists():
        models = StoreConsultant.objects.filter(
            query & Q(team_mgr__icontains=request.user.username)).distinct().order_by('id')

    else:
        models = StoreConsultant.objects.none()  # No access for other users

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
        'page_number': page_number,
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
        store = StoreConsultant.objects.get(id=id)  # Use id to query the store
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
    page_number = request.GET.get('page')
    model = StoreConsultant.objects.get(id=id)
    form = StoreConsultantForm(instance=model)
    return render(request, 'store_consultant/edit.html', {'model': model, 'form': form, 'page_number': page_number})


# def update(request, id):
#     model = StoreConsultant.objects.get(id=id)
#     form = StoreConsultantForm(request.POST, instance=model)
#     if form.is_valid():
#         form.save()
#         return redirect("/store-index")
#     return render(request, 'store_consultant/edit.html', {'model': model})

def update(request, id):
    model = get_object_or_404(StoreConsultant, id=id)
    page_number = request.GET.get('page')
    print("----------------------")
    print(page_number)
    if page_number is not None:
        try:
            page_number = int(page_number)
        except ValueError:
            page_number = 1  # алдаатай тохиолдолд default
    else:
        page_number = 1  # параметр байхгүй үед default
    if request.method == 'POST':
        form = StoreConsultantForm(request.POST, instance=model)
        if form.is_valid():
            form.save()
            messages.info(request, 'SC information has been changed successfully!')
            return redirect(f"/store-index/?page={page_number}")  # Adjust the redirect URL as needed?
        else:
            print(form.errors)  # Print form errors in the console for debugging
    else:
        form = StoreConsultantForm(instance=model)

    return render(request, 'store_consultant/edit.html', {'form': form, 'model': model})


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


@login_required
def scIndex(request):
    current_date = datetime.datetime.now()
    current_year = current_date.year
    current_month = current_date.month

    next_three_years = [current_year]

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

    current_month_obj = months[current_month - 1]
    remaining_months = [current_month_obj]

    # Хамгийн сүүлийн хуваарилалт
    last_allocation = AllocationTemp.objects.order_by('-created_date').first()
    last_year = last_allocation.year if last_allocation else current_year
    last_month = last_allocation.month if last_allocation else current_month_obj['value']

    # 🧠 team_no -> "TEAM 1", "TEAM 2" гэх мэт CharField гэж үзээд тоон дарааллаар эрэмбэлнэ
    def extract_team_number(team_str):
        try:
            return int(team_str.strip().replace("TEAM", "").strip())
        except:
            return 9999  # fallback

    # Active areas sorted by team_no number
    areas = sorted(
        Area.objects.filter(is_active=True),
        key=lambda area: extract_team_number(area.team_no)
    )

    # SC тоо, Store тоог тус бүр area-р нь тоолох
    area_store_counts = {}
    for area in areas:
        scs = Consultants.objects.filter(allocationtemp__area=area).distinct()
        sc_count = scs.count()
        store_count = SC_Store_AllocationTemp.objects.filter(
            consultant__in=scs
        ).values('store_id').distinct().count()
        area_store_counts[area.id] = {
            'sc_count': sc_count,
            'store_count': store_count
        }

    # SC бүрийн store тоог тоолох
    consultants = Consultants.objects.filter(is_active=True).annotate(
        store_count=Count('store_allocations_temp')
    )

    # store_id, store_name-уудыг авах
    store_consultants = StoreConsultant.objects.filter(use_yn=1)
    store_id_and_name = store_consultants.values('store_id', 'store_name')

    context = {
        'areas': areas,
        'consultants': consultants,
        'store_consultants': store_consultants,
        'store_id_and_name': store_id_and_name,
        'next_three_years': next_three_years,
        'months': remaining_months,
        'last_year': last_year,
        'last_month': last_month,
        'area_store_counts': area_store_counts
    }

    return render(request, 'store_consultant/index.html', context)


def get_team_data(request, team_id):
    # Assuming team_id is passed correctly and you have a model Consultants with a related field allocation
    scs = Consultants.objects.filter(allocationtemp__area_id=team_id).values('id', 'sc_name')
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
        ~Q(store_id__in=SC_Store_AllocationTemp.objects.values_list('store__store_id', flat=True)),
        use_yn=1  # Include only active stores
    )
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
                store_cons = consultant
                # store_cons = Consultants.objects.get(sc_name=consultant.sc_name)

                # Fetch the area, set to None if 'not-allocated'
                area = Area.objects.get(id=area_id) if area_id != 'not-allocated' else None

                # Delete existing allocations for the consultant to avoid duplicates
                AllocationTemp.objects.filter(consultant=consultant).delete()

                # Create a new allocation
                AllocationTemp.objects.create(
                    consultant=consultant,
                    area=area,
                    store_cons=store_cons,
                    year=year,
                    month=month,
                    created_by=request.user,
                    modified_by=request.user
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


def sc_add_index(request):
    sc_name_query = request.GET.get('sc_name', '')

    # Build the query based on presence of filter values
    query = Q()
    if sc_name_query:
        query &= Q(sc_name__icontains=sc_name_query)

    models = Consultants.objects.filter(query).distinct().order_by('id')

    paginator = Paginator(models, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "store_consultant/sc_add_show.html", {
        'page_obj': page_obj,
        'sc_name_query': sc_name_query,
    })


# Create a new consultant
# def sc_add_new(request):
#     if request.method == "POST":
#         form = ConsultantFrom(request.POST)
#         if form.is_valid():
#             try:
#                 form.instance.created_by = request.user if not form.instance.pk else form.instance.created_by
#                 form.instance.modified_by = request.user
#                 form.save()
#                 messages.success(request, 'Form submission successful.')
#                 return redirect('/sc-add-index')
#             except Exception as e:
#                 # If save fails, add an error message and print the exception
#                 messages.error(request, 'Form could not be saved. Please try again.')
#                 print(f"Error saving form: {e}")
#         else:
#             # If form is not valid, show errors
#             for field, errors in form.errors.items():
#                 for error in errors:
#                     messages.error(request, f"Error in {field}: {error}")
#     else:
#         form = ConsultantFrom()
#
#     return render(request, 'store_consultant/sc_add_index.html', {
#         'form': form,
#     })


# Edit an existing consultant
# def sc_add_edit(request, id):
#     consultant = get_object_or_404(Consultants, id=id)
#     if request.method == 'POST':
#         form = ConsultantFrom(request.POST, instance=consultant)
#         if form.is_valid():
#             form.save()
#             return redirect('sc-add-index')
#     else:
#         form = ConsultantFrom(instance=consultant)
#     return render(request, 'store_consultant/sc_add_edit.html', {'form': form, 'consultant': consultant})


# Delete a consultant
# def sc_add_delete(request, id):
#     consultant = get_object_or_404(Consultants, id=id)
#     if request.method == 'POST':
#         consultant.delete()
#         return redirect('sc-add-index')
#     return render(request, 'store_consultant/sc_add_delete.html', {'consultant': consultant})


from django.views.decorators.http import require_POST
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
import traceback
from cupp.store_consultant.models import (
    AllocationTemp, SC_Store_AllocationTemp,
    Allocation, SC_Store_Allocation, HisAllocation
)


@require_POST
def push_data(request):
    try:
        with transaction.atomic():
            # Get all current entries in AllocationTemp
            temp_allocations = AllocationTemp.objects.all()
            temp_store_allocations = SC_Store_AllocationTemp.objects.all()

            # Set of store_cons and store for comparison
            temp_store_cons_ids = set(temp_allocations.values_list('store_cons', flat=True))
            temp_store_ids = set(temp_store_allocations.values_list('store', flat=True))

            # Update or create new entries in Allocation
            for temp in temp_allocations:
                Allocation.objects.update_or_create(
                    store_cons=temp.store_cons,
                    defaults={
                        'consultant': temp.consultant,
                        'area': temp.area,
                        'year': temp.year,
                        'month': temp.month,
                        'created_by': request.user,
                        'modified_by': request.user
                    }
                )

            # Update or create SC_Store_Allocation
            for temp_store in temp_store_allocations:
                SC_Store_Allocation.objects.update_or_create(
                    store=temp_store.store,
                    defaults={
                        'consultant': temp_store.consultant,
                        'store_name': temp_store.store_name,
                        'sc_name': temp_store.sc_name,
                        'store_no': temp_store.store_no
                    }
                )

            # Delete old entries
            Allocation.objects.filter(~Q(store_cons__in=temp_store_cons_ids)).delete()
            SC_Store_Allocation.objects.filter(~Q(store__in=temp_store_ids)).delete()

            # Insert into HisAllocation
            for allocation in Allocation.objects.all():
                if not allocation.consultant or not Consultants.objects.filter(id=allocation.consultant.id).exists():
                    continue

                sc_store_allocations = SC_Store_Allocation.objects.filter(consultant=allocation.consultant)

                for sc_store_allocation in sc_store_allocations:
                    HisAllocation.objects.create(
                        consultant=allocation.consultant,
                        store=sc_store_allocation.store,
                        store_name=sc_store_allocation.store_name or '',
                        sc_name=sc_store_allocation.sc_name or '',
                        store_no=sc_store_allocation.store_no or '',
                        year=allocation.year or '',
                        month=allocation.month or '',
                        team_no=allocation.team_no or '',
                        area=allocation.area,
                        store_cons=allocation.store_cons or '',
                        tags=allocation.tags or ''
                    )

        return JsonResponse({'status': 'success'})

    except Exception as e:
        traceback.print_exc()  # 👈 log full error to console
        return JsonResponse({'status': 'failed', 'message': str(e)}, status=500)


@csrf_protect
@require_POST
def save_consultant_stores(request):
    try:
        data = json.loads(request.body)
        print(f"Incoming payload: {data}")

        store_allocations = data.get("storeAllocations", [])
        removed_stores = data.get("removedStores", [])

        new_distribution = []
        deleted_allocations = []
        changed_allocations = []
        subtracted_allocations = []

        with transaction.atomic():
            existing_allocations = {
                (alloc.consultant.id, alloc.store.store_id): {
                    "id": alloc.id,
                    "consultant_id": alloc.consultant.id,
                    "consultant_name": alloc.sc_name
                }
                for alloc in SC_Store_AllocationTemp.objects.all()
            }

            consultant_store_count = {
                consultant_id: SC_Store_AllocationTemp.objects.filter(consultant_id=consultant_id).count()
                for consultant_id in SC_Store_AllocationTemp.objects.values_list("consultant_id", flat=True).distinct()
            }

            processed_consultants = set()

            all_current_allocations = {}
            for alloc in SC_Store_AllocationTemp.objects.all():
                all_current_allocations.setdefault(alloc.consultant.id, set()).add(alloc.store.store_id)

            for allocation in store_allocations:
                consultant_id = int(allocation["consultantId"])
                new_store_ids = set(allocation["storeIds"])

                current_store_ids = all_current_allocations.get(consultant_id, set())
                removed_store_ids = current_store_ids - new_store_ids

                if removed_store_ids:
                    removed_stores.append({"consultantId": consultant_id, "storeIds": list(removed_store_ids)})

            for removed in removed_stores:
                consultant_id = int(removed["consultantId"])
                store_ids = set(store_id.strip() for store_id in removed["storeIds"] if store_id.strip())
                processed_consultants.add(consultant_id)

                if store_ids:
                    SC_Store_AllocationTemp.objects.filter(
                        consultant_id=consultant_id, store__store_id__in=store_ids
                    ).delete()

                    deleted_allocations.extend(
                        [{"store_id": store_id, "consultant_id": consultant_id} for store_id in store_ids]
                    )

            for allocation in store_allocations:
                consultant_id = int(allocation["consultantId"])
                store_ids = set(store_id.strip() for store_id in allocation["storeIds"] if store_id.strip())
                processed_consultants.add(consultant_id)

                for store_id in store_ids:
                    store = StoreConsultant.objects.get(store_id=store_id)
                    consultant = Consultants.objects.get(id=consultant_id)

                    # ✅ Always delete existing allocation of this store from any consultant
                    SC_Store_AllocationTemp.objects.filter(store__store_id=store_id).delete()

                    # Then create new allocation
                    new_allocation = SC_Store_AllocationTemp.objects.create(
                        consultant=consultant,
                        store=store,
                        sc_name=consultant.sc_name,
                        store_no=store.store_id,
                        store_name=store.store_name,
                    )
                    new_distribution.append({
                        "store_id": new_allocation.store.store_id,
                        "consultant_id": new_allocation.consultant.id,
                        "consultant_name": new_allocation.consultant.sc_name,
                    })

            for consultant_id in processed_consultants:
                new_store_count = SC_Store_AllocationTemp.objects.filter(consultant_id=consultant_id).count()
                previous_store_count = consultant_store_count.get(consultant_id, 0)

                if previous_store_count > new_store_count:
                    subtracted_allocations.append({
                        "consultant_id": consultant_id,
                        "removed_count": previous_store_count - new_store_count,
                        "message": f"{previous_store_count - new_store_count} stores removed for consultant {consultant_id}",
                    })

                if new_store_count == 0 and previous_store_count > 0:
                    SC_Store_AllocationTemp.objects.filter(consultant_id=consultant_id).delete()
                    deleted_allocations.append({
                        "consultant_id": consultant_id,
                        "message": f"All stores removed for consultant {consultant_id}"
                    })

            print("\nNew Allocations:", new_distribution)
            print("\nDeleted Allocations:", deleted_allocations)
            print("\nChanged Allocations:", changed_allocations)
            print("\nSubtracted Allocations:", subtracted_allocations)

        return JsonResponse({
            "status": "success",
            "message": "Allocations saved successfully.",
            "new_allocations": new_distribution,
            "deleted_allocations": deleted_allocations,
            "changed_allocations": changed_allocations,
            "subtracted_allocations": subtracted_allocations,
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"status": "failed", "message": str(e)}, status=500)


def get_allocations(request):
    allocations = AllocationTemp.objects.all().values('id', 'consultant__id', 'area__id', 'year', 'month')
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
    scs = Consultants.objects.filter(allocationtemp__area_id=team_id)
    sc_data = []

    # Get a list of already allocated stores (across all consultants)
    allocated_stores = SC_Store_AllocationTemp.objects.values_list('store__store_id', flat=True).distinct()

    for sc in scs:
        # Get the store IDs and names allocated to the consultant
        store_allocations = SC_Store_AllocationTemp.objects.filter(consultant=sc)
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


@csrf_exempt
def clear_allocations(request):
    if request.method == 'POST':
        try:
            # Delete all records in the Allocation table
            AllocationTemp.objects.all().delete()
            return JsonResponse({'status': 'success', 'message': 'All SC allocations cleared.'})
        except Exception as e:
            return JsonResponse({'status': 'failed', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'failed', 'message': 'Invalid request method.'}, status=400)


@require_GET
def search_store_allocation(request):
    store_id = request.GET.get('store_id', '').strip()
    if not store_id:
        return JsonResponse({'status': 'failed', 'message': 'No store ID provided'}, status=400)

    try:
        allocation = SC_Store_AllocationTemp.objects.select_related('store', 'consultant').filter(
            store__store_id=store_id).first()

        if not allocation:
            return JsonResponse({
                'status': 'failed',
                'message': f'Store ID {store_id} not found in SC_Store_AllocationTemp.'
            }, status=404)

        consultant_id = allocation.consultant_id

        # AllocationTemp бичлэгүүд
        allocation_temps = AllocationTemp.objects.filter(consultant_id=consultant_id).exclude(area_id__isnull=True)

        area_ids = allocation_temps.values_list('area_id', flat=True).distinct()
        areas = Area.objects.filter(id__in=area_ids).values('team_no', 'team_man_name')

        return JsonResponse({
            'status': 'success',
            'data': {
                'store_no': allocation.store_no,
                'store_name': allocation.store_name,
                'sc_name': allocation.sc_name,
                'teams': list(areas)  # ← frontend-д тохируулах
            }
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'status': 'failed',
            'message': 'Server error occurred while processing your request.'
        }, status=500)


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
# populate_historical_allocations()

# def get_unallocated_stores(request):
#     unallocated_stores = StoreConsultant.objects.filter(allocation__isnull=True)
#     store_data = [{'store_id': store.store_id} for store in unallocated_stores]
#     return JsonResponse({'stores': store_data})


@login_required
def lock_list(request):
    """
    Lock UI-г харуулах view. Салбарын дугаараар хайлт хийж болно.
    """
    store_id_query = request.GET.get('store_id', '')

    query = Q()
    if store_id_query:
        query &= Q(store_id__icontains=store_id_query)

    queryset = StoreConsultant.objects.filter(query).order_by('id')

    paginator = Paginator(queryset, 10)  # 10 мөрөөр хуудаслаж харуулна
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'store_consultant/lock.html', {
        'page_obj': page_obj,
        'store_id_query': store_id_query
    })

@require_POST
@login_required
def lock_update(request):
    lock_ids_sc = request.POST.getlist('lock_ids_sc')
    lock_ids_sp = request.POST.getlist('lock_ids_sp')
    lock_ids_st = request.POST.getlist('lock_ids_st')

    StoreConsultant.objects.update(
        is_locked_sc=False,
        is_locked_sp=False,
        is_locked_st=False
    )

    if lock_ids_sc:
        StoreConsultant.objects.filter(id__in=lock_ids_sc).update(is_locked_sc=True)
    if lock_ids_sp:
        StoreConsultant.objects.filter(id__in=lock_ids_sp).update(is_locked_sp=True)
    if lock_ids_st:
        StoreTrainer.objects.filter(id__in=lock_ids_st).update(is_locked_st=True)

    messages.success(request, "Lock тохиргоо амжилттай хадгалагдлаа.")
    return redirect('lock-list')