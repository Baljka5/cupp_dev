import re
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from cupp.store_consultant.models import StoreConsultant, Area, Consultants
from cupp.store_trainer.models import StoreTrainer
from cupp.point.models import Point, StorePlanning
from cupp.master_api.serializers import CompositeStoreSerializer
from cupp.master_api.mongo_util import get_bizloc_tp_by_cd
from django.http import JsonResponse


def update_store_type(request):
    store_id = request.GET.get('store_id')
    if not store_id:
        return JsonResponse({'status': 'error', 'message': 'Store ID is required'}, status=400)

    bizloc_tp = get_bizloc_tp_by_cd(store_id)

    if bizloc_tp is not None:
        store_consultant = StoreConsultant.objects.filter(store_id=store_id).first()
        if store_consultant:
            store_consultant.store_type = bizloc_tp
            store_consultant.save()
            return JsonResponse({'status': 'success', 'message': 'Store type updated'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Store consultant not found'}, status=404)
    else:
        return JsonResponse({'status': 'error', 'message': 'Business location not found'}, status=404)


class StoreMasterAPI(APIView):
    def get(self, request, *args, **kwargs):
        branch_no = request.query_params.get('branchNo', None)

        store_consultants = StoreConsultant.objects.filter(
            store_id=branch_no) if branch_no else StoreConsultant.objects.all()
        data = []

        if not store_consultants.exists() and branch_no:
            return Response({'message': 'Store not found', 'success': False}, status=status.HTTP_404_NOT_FOUND)

        for store_consultant in store_consultants:
            store_plannings = StorePlanning.objects.filter(store_id=store_consultant.store_id)
            store_trainer = StoreTrainer.objects.filter(store_id=store_consultant.store_id).first()

            if not store_plannings.exists() or not store_trainer:
                continue

            branch_type = "Direct" if store_consultant.store_type == 0 else "Franchise"
            wday_hours = store_consultant.wday_hours or "00:00-23:59"
            time_format = r"^\d{2}:\d{2}:\d{2}$"

            if re.match(time_format, wday_hours):
                open_time, close_time = None, None
            else:
                open_time, close_time = wday_hours.split('-')

            is_24h_open = store_consultant.tt_type == "24H" if store_consultant else False

            sc_name = store_consultant.sc_name or ""
            branch_employee_name = "N/A"
            sc_surname = None
            if "@cumongol.mn" in sc_name:
                sc_name_part = sc_name.split("@")[0]
                branch_employee_name = " ".join(word.capitalize() for word in sc_name_part.split("."))

                sc = Consultants.objects.filter(sc_email=sc_name).first()
                if sc:
                    sc_surname = sc.sc_surname

            area_name = store_consultant.team_mgr or ""
            area_branch_employee_name = "N/A"
            branch_area_surname = None  # Initialize the branchAreaSurname as None
            if "@cumongol.mn" in area_name:
                area_name_part = area_name.split("@")[0]
                area_branch_employee_name = " ".join(word.capitalize() for word in area_name_part.split("."))
                # Query the Area model using the email to get the surname
                area_manager = Area.objects.filter(team_man_email=area_name).first()
                if area_manager:
                    branch_area_surname = area_manager.team_man_surname


            store_id_stripped = store_consultant.store_id.lstrip('0') if store_consultant.store_id else None
            store_email_prefix = "cu" if store_consultant.store_type == 0 else "cuf"
            store_email = f"{store_email_prefix}{store_id_stripped}@cumongol.mn"

            employees_data = [{
                'position': "Дэлгүүрийн менежер",
                'name': store_consultant.sm_name if store_consultant else "N/A",
                'phone': store_consultant.sm_phone if store_consultant else "",
            }]

            lat = None
            lon = None
            for store_planning in store_plannings:
                if store_planning.lat and store_planning.lon:
                    lat = store_planning.lat
                    lon = store_planning.lon
                    break  # Assuming there is only one matching store_planning per store_id

            area_manager_phone = None
            if store_consultant.team_mgr and area_manager:
                area_manager_phone = area_manager.team_man_phone

            sc_phone = None
            if store_consultant.sc_name:
                sc = Consultants.objects.filter(sc_email=store_consultant.sc_name).first()  # Use .first() to get the first matching instance
                if sc:
                    sc_phone = sc.sc_phone

            data.append({
                'branchType': branch_type,
                'branchNo': store_consultant.store_id,
                'branchAddress': store_planning.address_det if store_planning else None,
                'branchName': store_consultant.store_name,
                'branchOpeningDate': store_trainer.open_date if store_trainer else None,
                'branchInChargeEmail': store_consultant.sc_name,
                'branchInChargeName': branch_employee_name,
                'branchInChargePhone': sc_phone,
                'areaManagerName': area_branch_employee_name,
                'branchInChargeSurname': sc_surname,
                'areaManagerEmail': store_consultant.team_mgr,
                'areaManagerPhone': area_manager_phone,
                'branchAreaSurname': branch_area_surname,  # Add the surname to the response
                'branchEmployees': employees_data,
                'openTime': open_time,
                'closeTime': close_time,
                'roZone': store_planning.cluster if store_planning else '',
                'storeEmail': store_email,
                'is24Open': is_24h_open,
                'isClose': bool(store_consultant.close_date),
                'closeDate': store_consultant.close_date,
                'lat': lat,
                'long': lon,
            })

        if not data:
            return Response({'message': 'Store not found', 'success': False}, status=status.HTTP_404_NOT_FOUND)

        serializer = CompositeStoreSerializer(data, many=True)
        return Response(serializer.data)
