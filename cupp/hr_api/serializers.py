from rest_framework import serializers
from cupp.point.models import StorePlanning
from cupp.store_trainer.models import StoreTrainer
from cupp.store_consultant.models import StoreConsultant, Consultants, Area, SC_Store_Allocation


class StorePlanningSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorePlanning
        fields = [
            'grade', 'address', 'cluster', 'addr1_prov', 'addr2_dist', 'addr3_khr', 'address', 'sp_name', 'near_school',
            'address_simple'
        ]


class StoreTrainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreTrainer
        fields = [
            'st_name', 'displayed_date', 'planned_date', 'open_date', 'open_time', 'created_date'
        ]


class StoreConsultantSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreConsultant
        fields = [
            'store_id', 'store_name', 'team_mgr', 'sc_name', 'sm_num', 'am_num',
            'tt_type', 'wday_hours', 'wend_hours', 'alc_reason', 'ciga_reason',
            'close_date', 'close_reason', 'sm_name', 'sm_phone', 'created_date',
            'out_city_flow', 'in_out_flow', 'near_bus_station', 'bus_station_range',
            'university_range', 'high_school_range'
        ]


class SCAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SC_Store_Allocation
        # fields = ['store_name', 'sc_name', 'store_no', 'created_date', 'modified_date']
        fields = '__all__'


class ConsultantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultants
        fields = '__all__'


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = '__all__'
