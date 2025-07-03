import requests
import json
from numpy import record
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from sentry_sdk.serializer import serialize
import traceback

from cupp.point.models import StorePlanning, City, District
from cupp.veritech_api.models import General, Experience
from cupp.store_trainer.models import StoreTrainer
from cupp.store_consultant.models import (
    StoreConsultant, SC_Store_AllocationTemp, Consultants, AllocationTemp, Area
)
from .serializers import (
    StorePlanningSerializer, StoreTrainerSerializer, StoreConsultantSerializer,
    SCAllocationSerializer, CitySerializer, DistrictSerializer, VeritechGeneralSerializer, PersonalInfoRawSerializer,
    PersonalInfoRaw, EmpPersonalInfoRawSerializer, EmpPersonalInfoRaw
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

        exp_qs_all = Experience.objects.all()
        exp_qs_current = Experience.objects.filter(enddate__isnull=True)

        exp_map = {}
        exp_full_map = {}

        for exp in exp_qs_current:
            key = str(exp.employeeid)
            exp_map.setdefault(key, []).append((exp.departmentname, exp.positionname))

        for exp in exp_qs_all:
            key = str(exp.employeeid)
            exp_full_map.setdefault(key, []).append({
                "startdate": exp.startdate,
                "enddate": exp.enddate,
                "departmentname": exp.departmentname
            })

        serializer = VeritechGeneralSerializer(
            records,
            many=True,
            context={
                "experience_map": exp_map,
                "experience_full_map": exp_full_map
            }
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class SaveRawJsonView(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = []

    def post(self, request):
        try:
            original_data = request.data.copy()

            incoming_data = {
                "data": json.dumps(original_data),
                "employee_id": original_data.get("employee_id", ""),
                "responseData": None
            }

            serializer = PersonalInfoRawSerializer(data=incoming_data)
            if serializer.is_valid():
                instance = serializer.save()

                headers = {
                    "x-api-key": request.META.get("HTTP_X_API_KEY", "")
                }

                # 1-р API
                first_api_url = "https://pp.cumongol.mn/api/list-data/"
                try:
                    first_response = requests.get(first_api_url, headers=headers, timeout=50, verify=False)
                    first_json = first_response.json() if 'application/json' in first_response.headers.get(
                        'Content-Type', '') else {"raw": first_response.text}
                except Exception as ex:
                    first_json = {"error": f"Request to pp.cumongol.mn failed: {str(ex)}"}

                # Хэрвээ list хэлбэртэй байвал эхний dict-г сонгоно
                if isinstance(first_json, list):
                    if len(first_json) > 0 and isinstance(first_json[0], dict):
                        payload_to_candidate = first_json[0]
                    else:
                        payload_to_candidate = {"error": "Invalid list structure from first API"}
                else:
                    payload_to_candidate = first_json

                # 2-р API
                second_api_url = "http://10.10.90.90/candidate/"
                second_response = None
                try:
                    second_response = requests.post(second_api_url, json=payload_to_candidate, headers=headers,
                                                    timeout=50)
                    second_json = second_response.json() if 'application/json' in second_response.headers.get(
                        'Content-Type', '') else {"raw": second_response.text}
                except Exception as ex:
                    second_json = {"error": f"Request to internal API failed: {str(ex)}"}

                # Final data structure
                try:
                    current_data = json.loads(instance.data)
                except Exception:
                    current_data = {
                        "original": original_data,
                    }

                # Save back to DB
                instance.data = json.dumps(current_data)
                instance.responseData = json.dumps(second_json)
                instance.status = "SUCCESS" if second_response and second_response.status_code == 200 else "ERROR"
                instance.save()

                return Response({
                    "message": "Data saved and forwarded successfully",
                    "data": current_data,
                    "responseData": second_json
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
            records = PersonalInfoRaw.objects.filter(status="Pending").order_by('-created_at')[:50]
            serializer = PersonalInfoRawSerializer(records, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": str(e),
                "traceback": traceback.format_exc()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmpPersonalInfoListView(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = []

    def get(self, request):
        try:
            records = EmpPersonalInfoRaw.objects.filter(status="Pending").order_by('-created_at')[:50]
            serializer = EmpPersonalInfoRawSerializer(records, many=True)
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

    def post(self, request, pk):
        try:
            instance = PersonalInfoRaw.objects.get(id=pk)

            payload = request.data

            url = "https://pp.cumongol.mn/api/list-info/"
            headers = {
                "x-api-key": self.request.META.get("HTTP_X_API_KEY", "")
            }

            response = requests.post(url, json=payload, headers=headers, timeout=10, verify=False)

            # Parse response (not stored in responseData)
            if response.headers.get('Content-Type', '').startswith('application/json'):
                response_json = response.json()
            else:
                response_json = {"raw": response.text}

            # Save only request payload to responseData
            instance.responseData = json.dumps(payload)
            instance.status = "SUCCESS" if response.status_code == 200 else "ERROR"
            instance.save()

            # Parse saved `data`
            try:
                stored_data = json.loads(instance.data)
            except Exception:
                stored_data = {"error": "Invalid stored data"}

            return Response({
                "data": stored_data,
                "responseData": payload
            }, status=status.HTTP_200_OK)

        except PersonalInfoRaw.DoesNotExist:
            return Response({"error": "Record not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "error": str(e),
                "traceback": traceback.format_exc()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FetchAndUpdateFromExternalView(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = []

    def post(self, request):
        try:
            headers = {
                "x-api-key": request.META.get("HTTP_X_API_KEY", "")
            }

            list_data_url = "https://pp.cumongol.mn/api/list-data/"

            try:
                response = requests.get(list_data_url, headers=headers, timeout=30, verify=False)
                print("✅ Response status code:", response.status_code)
                print("✅ Response headers:", response.headers)
                print("✅ Raw response text:", response.text)

                content_type = response.headers.get("Content-Type", "")
                if content_type.startswith("application/json"):
                    response_data = response.json()
                else:
                    print("⚠️ Unexpected Content-Type:", content_type)
                    return Response({"error": f"Unexpected Content-Type: {content_type}"}, status=500)

            except Exception as e:
                return Response({"error": f"Failed to fetch from list-data API: {str(e)}"}, status=500)

            # ⛔ If response is empty list
            if not isinstance(response_data, list) or len(response_data) == 0:
                return Response({
                    "message": "Response received but no data found",
                    "data_preview": response_data
                }, status=200)

            result = []

            # 2. Iterate and update each entry
            for item in response_data:
                employee_id = item.get("employee_id", "")
                if not employee_id:
                    result.append({
                        "status": "SKIPPED",
                        "reason": "Missing employee_id",
                        "item": item
                    })
                    continue

                try:
                    instance = PersonalInfoRaw.objects.filter(employee_id=employee_id).latest('created_at')
                except PersonalInfoRaw.DoesNotExist:
                    result.append({
                        "employee_id": employee_id,
                        "status": "SKIPPED",
                        "reason": "No existing record found"
                    })
                    continue

                # 3. Forward to candidate API
                candidate_url = "http://10.10.90.90/candidate/"
                try:
                    post_response = requests.post(candidate_url, json=item, headers=headers, timeout=30)
                    content_type_post = post_response.headers.get('Content-Type', '')
                    if content_type_post.startswith("application/json"):
                        post_json = post_response.json()
                    else:
                        post_json = {"raw": post_response.text}
                except Exception as e:
                    post_json = {"error": f"POST to candidate failed: {str(e)}"}
                    instance.status = "ERROR"
                else:
                    instance.status = "SUCCESS" if post_response.status_code == 200 else "ERROR"

                # 4. Update DB instance
                instance.responseData = json.dumps(post_json)
                instance.save()

                result.append({
                    "updated_id": instance.id,
                    "employee_id": employee_id,
                    "status": instance.status
                })

            return Response({
                "message": "Processed all matched records",
                "results": result
            }, status=200)

        except Exception as e:
            return Response({
                "error": str(e),
                "traceback": traceback.format_exc()
            }, status=500)


class SaveOnlyRawJsonView(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = []

    def post(self, request):
        try:
            original_data = request.data.copy()

            instance = PersonalInfoRaw.objects.create(
                unique_id=original_data.get("unique_id", ""),
                data=json.dumps(original_data),
                employee_id=original_data.get("employee_id", ""),
                responseData=None,
                status="Pending"
            )

            return Response({
                "message": "Data saved successfully",
                "unique_id": instance.unique_id
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                "error": str(e),
                "traceback": traceback.format_exc()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmpSaveOnlyRawJsonView(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = []

    def post(self, request):
        try:
            original_data = request.data.copy()

            instance = EmpPersonalInfoRaw.objects.create(
                data=json.dumps(original_data),
                employee_id=original_data.get("employee_id", ""),
                responseData=None,
                status="Pending"
            )

            return Response({
                "message": "Data saved successfully",
                "id": instance.id,
                "employee_id": instance.employee_id
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                "error": str(e),
                "traceback": traceback.format_exc()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PersonalInfoMergedView(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = []

    def get(self, request, unique_id):
        try:
            instance = PersonalInfoRaw.objects.filter(unique_id=unique_id).latest('created_at')

            try:
                data_json = json.loads(instance.data)
            except Exception:
                data_json = {"error": "Invalid data JSON"}

            try:
                response_json = json.loads(instance.responseData) if instance.responseData else {}
            except Exception:
                response_json = {"error": "Invalid responseData JSON"}

            # Combine both
            merged = {
                "data": data_json,
                "responseData": response_json
            }

            return Response(merged, status=200)

        except PersonalInfoRaw.DoesNotExist:
            return Response({"error": "Record not found"}, status=404)
        except Exception as e:
            return Response({
                "error": str(e),
                "traceback": traceback.format_exc()
            }, status=500)


class EmpPersonalInfoMergedView(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = []

    def get(self, request, pk):
        try:
            instance = EmpPersonalInfoRaw.objects.get(id=pk)

            try:
                data_json = json.loads(instance.data)
            except Exception:
                data_json = {"error": "Invalid data JSON"}

            try:
                response_json = json.loads(instance.responseData) if instance.responseData else {}
            except Exception:
                response_json = {"error": "Invalid responseData JSON"}

            # Combine both
            merged = {
                "data": data_json,
                "responseData": response_json,
                "status": instance.status,
                "employee_id": instance.employee_id,
                "created_at": instance.created_at
            }

            return Response(merged, status=200)

        except EmpPersonalInfoRaw.DoesNotExist:
            return Response({"error": "Record not found"}, status=404)
        except Exception as e:
            return Response({
                "error": str(e),
                "traceback": traceback.format_exc()
            }, status=500)
