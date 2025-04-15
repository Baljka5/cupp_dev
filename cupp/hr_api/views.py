from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from cupp.point.models import StorePlanning
from cupp.store_trainer.models import StoreTrainer
from cupp.store_consultant.models import (
    StoreConsultant, SC_Store_Allocation, Consultants, Allocation, Area
)
from .serializers import (
    StorePlanningSerializer, StoreTrainerSerializer, StoreConsultantSerializer,
    SCAllocationSerializer,
)


class StoreListCombinedInfoView(APIView):
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
            sc_allocations = SC_Store_Allocation.objects.filter(store__store_id=store_id)
            entry['sc_store_allocations'] = SCAllocationSerializer(sc_allocations, many=True).data

            data.append(entry)

        return Response(data, status=status.HTTP_200_OK)


class StoreCombinedInfoView(APIView):
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
        sc_allocations = SC_Store_Allocation.objects.filter(store__store_id=store_id)
        data['sc_store_allocations'] = SCAllocationSerializer(sc_allocations, many=True).data

        # 5. Consultants (from allocations)
        consultant_ids = sc_allocations.values_list('consultant_id', flat=True).distinct()
        consultants = Consultants.objects.filter(id__in=consultant_ids)
        # data['consultants'] = ConsultantSerializer(consultants, many=True).data

        # 6. Allocation (from consultant_id)
        allocations = Allocation.objects.filter(consultant_id__in=consultant_ids)
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
