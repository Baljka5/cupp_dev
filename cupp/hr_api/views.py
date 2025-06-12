import requests
import json
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
    SCAllocationSerializer, CitySerializer, DistrictSerializer, VeritechGeneralSerializer, PersonalInfoRawSerializer,
    PersonalInfoRaw
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


class SaveRawJsonView(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = []

    def post(self, request):
        try:
            # JSON string болгож дамжуулж байна
            incoming_data = {
                "data": json.dumps(request.data),
                "employee_id": request.data.get("employee_id", ""),
                "responseData": json.dumps(request.data.get("responseData", {}))
            }

            serializer = PersonalInfoRawSerializer(data=incoming_data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Data saved successfully",
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "error": str(e),
                "traceback": traceback.format_exc()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PersonalInfoListView(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = []

    def get(self, request):
        try:
            records = PersonalInfoRaw.objects.order_by('-created_at')[:50]
            serializer = PersonalInfoRawSerializer(records, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": str(e),
                "traceback": traceback.format_exc()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ListDataView(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = []

    def post(self, request):
        payload = request.data
        return Response({
            "status": "SUCCESS",
            "employee_id": payload.get("employee_id", ""),
            "error_message": ""
        }, status=200)


class ForwardPersonalInfoView(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = []

    def put(self, request, pk):
        try:
            instance = PersonalInfoRaw.objects.get(id=pk)

            # Хадгалсан JSON string-ийг dict болгон хөрвүүлнэ
            try:
                payload = json.loads(instance.data)
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON in stored data"}, status=400)

            url = "https://pp.cumongol.mn/api/list-info/"

            headers = {
                "x-api-key": self.request.META.get("HTTP_X_API_KEY", "")
            }

            response = requests.post(url, json=payload, headers=headers, timeout=10, verify=False)

            # Хариу нь JSON хэлбэртэй байвал responseData-д dict хэлбэрээр хадгална
            if response.headers.get('Content-Type', '').startswith('application/json'):
                instance.responseData = response.json()
            else:
                instance.responseData = {"raw": response.text}

            instance.status = "SUCCESS" if response.status_code == 200 else "ERROR"
            instance.save()

            return Response({
                "status": instance.status,
                "response_status": response.status_code,
                "response_data": instance.responseData,
            }, status=status.HTTP_200_OK)

        except PersonalInfoRaw.DoesNotExist:
            return Response({"error": "Record not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "error": str(e),
                "traceback": traceback.format_exc()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

