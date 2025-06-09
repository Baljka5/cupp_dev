import requests
from numpy import record
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from sentry_sdk.serializer import serialize
import traceback

from cupp.point.models import StorePlanning, City, District
from cupp.veritech_api.models import General
from cupp.store_trainer.models import StoreTrainer
from cupp.store_consultant.models import (
    StoreConsultant, SC_Store_AllocationTemp, Consultants, AllocationTemp, Area
)
from .serializers import (
    StorePlanningSerializer, StoreTrainerSerializer, StoreConsultantSerializer,
    SCAllocationSerializer, CitySerializer, DistrictSerializer, VeritechGeneralSerializer, PersonalInfoSerializer
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.authentication import SessionAuthentication
from .authentication import APIKeyAuthentication


class StoreListCombinedInfoView(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = []

    def get(self, request):
        data = []

        store_ids = StoreConsultant.objects.values_list('store_id', flat=True).distinct()

        for store_id in store_ids:
            entry = {}

            # 1. StorePlanning
            planning = StorePlanning.objects.filter(store_id=store_id).first()
            entry['store_planning'] = StorePlanningSerializer(planning).data if planning else None

            # 2. StoreTrainer
            trainer = StoreTrainer.objects.filter(store_id=store_id).first()
            entry['store_trainer'] = StoreTrainerSerializer(trainer).data if trainer else None

            # 3. StoreConsultant
            consultant = StoreConsultant.objects.filter(store_id=store_id).first()
            entry['store_consultant'] = StoreConsultantSerializer(consultant).data if consultant else None

            # 4. SC_Store_Allocation
            sc_allocations = SC_Store_AllocationTemp.objects.filter(store__store_id=store_id)
            entry['sc_store_allocations'] = SCAllocationSerializer(sc_allocations, many=True).data

            data.append(entry)

        return Response(data, status=status.HTTP_200_OK)


class StoreCombinedInfoView(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = []

    def get(self, request, store_id):
        data = {}

        # 1. StorePlanning
        planning = StorePlanning.objects.filter(store_id=store_id).first()
        data['store_planning'] = StorePlanningSerializer(planning).data if planning else None

        # 2. StoreTrainer
        trainer = StoreTrainer.objects.filter(store_id=store_id).first()
        data['store_trainer'] = StoreTrainerSerializer(trainer).data if trainer else None

        # 3. StoreConsultant
        consultant = StoreConsultant.objects.filter(store_id=store_id).first()
        data['store_consultant'] = StoreConsultantSerializer(consultant).data if consultant else None

        # 4. SC_Store_Allocation
        sc_allocations = SC_Store_AllocationTemp.objects.filter(store__store_id=store_id)
        data['sc_store_allocations'] = SCAllocationSerializer(sc_allocations, many=True).data

        # 5. Consultants (from allocations)
        consultant_ids = sc_allocations.values_list('consultant_id', flat=True).distinct()
        consultants = Consultants.objects.filter(id__in=consultant_ids)
        # data['consultants'] = ConsultantSerializer(consultants, many=True).data

        # 6. Allocation (from consultant_id)
        allocations = AllocationTemp.objects.filter(consultant_id__in=consultant_ids)
        # data['allocations'] = [
        #     {
        #         "id": alloc.id,
        #         "storeID": alloc.storeID,
        #         "store_name": alloc.store_name,
        #         "store_cons": alloc.store_cons,
        #         "team_no": alloc.team_no,
        #         "year": alloc.year,
        #         "month": alloc.month,
        #         "area_id": alloc.area_id
        #     }
        #     for alloc in allocations
        # ]

        # 7. Area (from allocation.area_id)
        area_ids = allocations.values_list('area_id', flat=True).distinct()
        areas = Area.objects.filter(id__in=area_ids)
        # data['areas'] = AreaSerializer(areas, many=True).data

        return Response(data, status=status.HTTP_200_OK)


class StoreAddressInfoView(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = []

    def get(self, request):
        cities = City.objects.all()
        districts = District.objects.select_related('city').all()

        data = {
            "cities": CitySerializer(cities, many=True).data,
            "districts": DistrictSerializer(districts, many=True).data
        }

        return Response(data, status=status.HTTP_200_OK)


class VeritechGeneralView(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = []

    def get(self, request):
        records = General.objects.all()
        serializer = VeritechGeneralSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class ForwardPersonalInfoView(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = []

    def post(self, request):
        try:
            sample_data = [
                {
                    "first_name": "Дархан",
                    "last_name": "Атарболд",
                    "email": "darkhan20021@gmail.com",
                    "family_name": "",
                    "birthday": "2009-06-05T16:34:35.000Z",
                    "register_number": "ЖЖ80888811",
                    "workplace_code": "00120",
                    "workplace_name": "Цагийн ажилтан",
                    "unit_code": "CU120",
                    "start_date": "2025-06-05T16:35:00.567Z",
                    "gender": "MALE",
                    "phone_number": "86008112",
                    "civil_reg_number": "",
                    "bank_account_number": "",
                    "bank_name": "",
                    "address_type1": "",
                    "city1": "Баян-Өлгий",
                    "district1": "Алтанцөгц",
                    "committee1": "2-р баг, Баянбулаг",
                    "address1": "өбб",
                    "address_type2": "",
                    "city2": "",
                    "district2": "",
                    "committee2": "",
                    "address2": ""
                },
                {
                    "first_name": "Дархан2",
                    "last_name": "Атарболд2",
                    "email": "darkhan20021@gmail.com",
                    "family_name": "",
                    "birthday": "2009-06-05T16:34:35.000Z",
                    "register_number": "ЖЖ80888811",
                    "workplace_code": "00120",
                    "workplace_name": "Цагийн ажилтан",
                    "unit_code": "CU120",
                    "start_date": "2025-06-05T16:35:00.567Z",
                    "gender": "MALE",
                    "phone_number": "86008112",
                    "civil_reg_number": "",
                    "bank_account_number": "",
                    "bank_name": "",
                    "address_type1": "",
                    "city1": "Баян-Өлгий",
                    "district1": "Алтанцөгц",
                    "committee1": "2-р баг, Баянбулаг",
                    "address1": "өбб",
                    "address_type2": "",
                    "city2": "",
                    "district2": "",
                    "committee2": "",
                    "address2": ""
                },

            ]

            serializer = PersonalInfoSerializer(data=sample_data, many=True)
            if serializer.is_valid():
                return Response({
                    "status": "success (test mode)",
                    "data_sent": serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "error": str(e),
                "traceback": traceback.format_exc()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class ForwardPersonalInfoView(APIView):
#     authentication_classes = [APIKeyAuthentication]
#     permission_classes = []
#
#     def post(self, request):
#         serializer = PersonalInfoSerializer(data=request.data, many=True)
#         if serializer.is_valid():
#             # Гадаад API руу дамжуулах
#             external_api_url = "https://external.example.com/endpoint"
#             headers = {
#                 "Content-Type": "application/json",
#                 "Authorization": "Bearer your_token_here"
#             }
#
#             try:
#                 response = requests.post(external_api_url, json=serializer.data, headers=headers)
#                 return Response({
#                     "status": "forwarded",
#                     "external_status_code": response.status_code,
#                     "external_response": response.json()
#                 }, status=status.HTTP_200_OK)
#
#             except requests.exceptions.RequestException as e:
#                 return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
