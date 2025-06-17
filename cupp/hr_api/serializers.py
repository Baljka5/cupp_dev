from rest_framework import serializers
from cupp.point.models import StorePlanning, City, District
from cupp.store_trainer.models import StoreTrainer
from cupp.store_consultant.models import StoreConsultant, Consultants, Area, SC_Store_AllocationTemp, AllocationTemp
from cupp.veritech_api.models import General, Experience
from cupp.hr_api.models import PersonalInfoRaw, EmpPersonalInfoRaw
import json


class StorePlanningSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorePlanning
        fields = [
            'grade', 'address_det', 'cluster', 'addr1_prov', 'addr2_dist', 'addr3_khr', 'address', 'near_school',
            'address_simple', 'lat', 'lon'
        ]


class StoreTrainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreTrainer
        fields = [
            'st_name', 'displayed_date', 'planned_date'
        ]


class StoreConsultantSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreConsultant
        fields = [
            'store_id', 'store_name', 'team_mgr', 'sc_name', 'sm_num', 'am_num',
            'tt_type', 'wday_hours', 'wend_hours', 'alc_reason', 'ciga_reason', 'sm_name', 'sm_phone', 'created_date',
            'out_city_flow', 'in_out_flow', 'near_bus_station', 'bus_station_range',
            'university_range', 'high_school_range', 'use_yn', 'store_type', 'store_email', 'ost_dt'
        ]


class SCAllocationSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField()
    sc_name = serializers.CharField()
    store_no = serializers.CharField()
    sc_email = serializers.SerializerMethodField()
    sc_code = serializers.SerializerMethodField()  # ← нэмсэн хэсэг

    year = serializers.SerializerMethodField()
    month = serializers.SerializerMethodField()
    area_team_no = serializers.SerializerMethodField()
    area_manager_name = serializers.SerializerMethodField()
    area_manager_surname = serializers.SerializerMethodField()
    area_manager_email = serializers.SerializerMethodField()

    class Meta:
        model = SC_Store_AllocationTemp
        fields = [
            'id',
            'store_name',
            'sc_name',
            'sc_code',  # ← шинэ талбар
            'store_no',
            'year',
            'month',
            'sc_email',
            'area_team_no',
            'area_manager_name',
            'area_manager_surname',
            'area_manager_email',
        ]

    def get_allocation(self, obj):
        if not hasattr(self, '_allocation_cache'):
            self._allocation_cache = {}
        key = obj.consultant_id
        if key not in self._allocation_cache:
            self._allocation_cache[key] = AllocationTemp.objects.filter(
                consultant_id=key
            ).select_related('area').first()
        return self._allocation_cache[key]

    def get_year(self, obj):
        allocation = self.get_allocation(obj)
        return allocation.year if allocation else None

    def get_month(self, obj):
        allocation = self.get_allocation(obj)
        return allocation.month if allocation else None

    def get_sc_email(self, obj):
        return obj.consultant.sc_email if obj.consultant else None

    def get_sc_code(self, obj):
        return obj.consultant.sc_code if obj.consultant else None

    def get_area_team_no(self, obj):
        allocation = self.get_allocation(obj)
        return allocation.area.team_no if allocation and allocation.area else None

    def get_area_manager_name(self, obj):
        allocation = self.get_allocation(obj)
        return allocation.area.team_man_name if allocation and allocation.area else None

    def get_area_manager_surname(self, obj):
        allocation = self.get_allocation(obj)
        return allocation.area.team_man_surname if allocation and allocation.area else None

    def get_area_manager_email(self, obj):
        allocation = self.get_allocation(obj)
        return allocation.area.team_man_email if allocation and allocation.area else None


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'city_code', 'city_name']


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['id', 'district_name', 'city']


class VeritechGeneralSerializer(serializers.ModelSerializer):
    department_names = serializers.SerializerMethodField()

    class Meta:
        model = General
        fields = ['employeeid', 'employeecode', 'gender', 'firstname', 'lastname', 'postaddress', 'department_names']

    def get_department_names(self, obj):
        experience_map = self.context.get("experience_map", {})
        return experience_map.get(str(obj.employeeid), [])


class PersonalInfoRawSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalInfoRaw
        fields = ['id', 'data', 'status', 'employee_id', 'responseData', 'created_at']

    def to_representation(self, instance):
        import json
        result = super().to_representation(instance)

        try:
            result['data'] = json.loads(result['data'])
        except Exception:
            result['data'] = {"error": "Invalid JSON"}

        try:
            result['responseData'] = json.loads(result['responseData']) if result['responseData'] else {}
        except Exception:
            result['responseData'] = {"error": "Invalid JSON"}

        return result

class EmpPersonalInfoRawSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmpPersonalInfoRaw
        fields = ['id', 'data', 'status', 'employee_id', 'responseData', 'created_at']

    def to_representation(self, instance):
        import json
        result = super().to_representation(instance)

        try:
            result['data'] = json.loads(result['data'])
        except Exception:
            result['data'] = {"error": "Invalid JSON"}

        try:
            result['responseData'] = json.loads(result['responseData']) if result['responseData'] else {}
        except Exception:
            result['responseData'] = {"error": "Invalid JSON"}

        return result
