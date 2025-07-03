from rest_framework import serializers
from cupp.point.models import StorePlanning, City, District
from cupp.store_trainer.models import StoreTrainer
from cupp.store_consultant.models import StoreConsultant, Consultants, Area, SC_Store_AllocationTemp, AllocationTemp
from cupp.veritech_api.models import General, Experience
from cupp.hr_api.models import PersonalInfoRaw, EmpPersonalInfoRaw
from datetime import date
import json
import re


class StorePlanningSerializer(serializers.ModelSerializer):
    address = serializers.SerializerMethodField()

    class Meta:
        model = StorePlanning
        fields = [
            'grade', 'address_det', 'cluster', 'addr1_prov', 'addr2_dist', 'addr3_khr',
            'address', 'near_school', 'address_simple', 'lat', 'lon'
        ]

    def get_address(self, obj):
        """
        Урд талын тоо болон . тэмдэгт арилгана (жишээ: '14. Сүхбаатарын гудамж' → 'Сүхбаатарын гудамж')
        """
        if not obj.address:
            return None
        return re.sub(r'^\s*\d+\.?\s*', '', obj.address.strip())


class StoreTrainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreTrainer
        fields = [
            'st_name', 'displayed_date', 'planned_date'
        ]


class StoreConsultantSerializer(serializers.ModelSerializer):
    cls_dt = serializers.SerializerMethodField()

    class Meta:
        model = StoreConsultant
        fields = [
            'store_id', 'store_name', 'team_mgr', 'sc_name', 'sm_num', 'am_num',
            'tt_type', 'wday_hours', 'wend_hours', 'alc_reason', 'ciga_reason', 'sm_name', 'sm_phone', 'created_date',
            'out_city_flow', 'in_out_flow', 'near_bus_station', 'bus_station_range',
            'university_range', 'high_school_range', 'use_yn', 'store_type', 'store_email', 'ost_dt', 'cls_dt'
        ]

    def get_cls_dt(self, obj):
        val = obj.cls_dt
        if not val:
            return None

        val_str = str(val).strip()
        if val_str.startswith("9999"):
            return 0

        return val


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
        original_code = obj.consultant.sc_code if obj.consultant else None
        allocation = self.get_allocation(obj)

        if not (allocation and allocation.area and original_code):
            return original_code  # fallback to default if any missing

        # area_team_no → "TEAM 2" → 2
        try:
            team_number = allocation.area.team_no.strip().split()[-1]
        except Exception:
            team_number = ""

        # sc_code → "SC5" → 5
        try:
            sc_number = original_code.strip().lstrip("SC")
        except Exception:
            sc_number = ""

        # Construct new format
        if team_number.isdigit() and sc_number.isdigit():
            return f"SC{team_number}-{sc_number}"
        else:
            return original_code

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
    department_name = serializers.SerializerMethodField()
    position_name = serializers.SerializerMethodField()
    store = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    total_years_worked = serializers.SerializerMethodField()
    joined_date = serializers.SerializerMethodField()
    cu_years_worked = serializers.SerializerMethodField()

    class Meta:
        model = General
        fields = [
            'employeeid', 'employeecode', 'urag', 'firstname', 'lastname',
            'gender', 'stateregnumber', 'dateofbirth', 'postaddress',
            'department_name', 'position_name', 'store',
            'type', 'status', 'age',
            'total_years_worked', 'joined_date', 'cu_years_worked'
        ]

    def get_experience_list(self, obj):
        experience_map_all = self.context.get("experience_full_map", {})
        return experience_map_all.get(str(obj.employeeid), [])

    def get_department_name(self, obj):
        experience = self.context.get("experience_map", {}).get(str(obj.employeeid), [])
        return experience[0][0] if experience else None

    def get_position_name(self, obj):
        experience = self.context.get("experience_map", {}).get(str(obj.employeeid), [])
        return experience[0][1] if experience else None

    def get_store(self, obj):
        dept_name = self.get_department_name(obj)
        if dept_name and dept_name.startswith("CU"):
            return dept_name
        return ""

    def get_type(self, obj):
        return obj.statusname

    def get_status(self, obj):
        return obj.currentstatusname

    def get_age(self, obj):
        if obj.dateofbirth:
            today = date.today()
            return today.year - obj.dateofbirth.year - (
                    (today.month, today.day) < (obj.dateofbirth.month, obj.dateofbirth.day)
            )
        return None

    def get_total_years_worked(self, obj):
        total_days = 0
        today = date.today()
        for exp in self.get_experience_list(obj):
            start = exp.get("startdate")
            end = exp.get("enddate") or today
            if start:
                total_days += (end - start).days

        return round(total_days / 365, 2) if total_days else 0

    def get_joined_date(self, obj):
        experience_list = self.get_experience_list(obj)
        if experience_list:
            start_dates = [exp['startdate'] for exp in experience_list if exp.get('startdate')]
            if start_dates:
                return min(start_dates)
        return None

    # def get_joined_date(self, obj):
    #     experience_list = self.get_experience_list(obj)
    #     start_dates = [exp['startdate'] for exp in experience_list if exp.get('startdate')]
    #     return min(start_dates) if start_dates else None

    def get_left_date(self, obj):
        experience_list = self.get_experience_list(obj)
        end_dates = [exp['enddate'] for exp in experience_list if exp.get('enddate')]
        return max(end_dates) if end_dates else None

    def get_cu_years_worked(self, obj):
        cu_days = 0
        today = date.today()
        for exp in self.get_experience_list(obj):
            dept = exp.get("departmentname", "")
            if dept.startswith("CU"):
                start = exp.get("startdate")
                end = exp.get("enddate") or today
                if start:
                    cu_days += (end - start).days

        return round(cu_days / 365, 2) if cu_days else 0


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
