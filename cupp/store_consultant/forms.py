from django import forms as f
from django.conf import settings
from cupp.store_consultant.models import StoreConsultant, Allocation, Tag, Consultants


class StoreConsultantForm(f.ModelForm):
    tags = f.ModelMultipleChoiceField(queryset=Tag.objects.all(), widget=f.CheckboxSelectMultiple, required=False)
    close_date = f.DateField(required=False, input_formats=settings.DATE_INPUT_FORMATS)
    CONSEQUENCES_CHOICES = [
        ('', '---------'),
        (True, 'Тийм'),
        (False, 'Үгүй'),
    ]
    ALC_TYPE = [
        ('', '--------'),
        (True, 'Чанга'),
        (False, 'Сул'),
    ]
    TOILET_TYPE_CHOICES = [
        ('', '---------'),
        (True, 'Нийтийн'),
        (False, 'Өөрийн'),
    ]
    TT_TYPE_CHOICES = [
        ('24H', '24H'),
        ('17H', '17H'),
        ('SPECIFIC', 'SPECIFIC')
    ]
    OUT_CITY_FLOW = [
        ('', '--------'),
        ('Орох', 'Орох'),
        ('Гарах', 'Гарах'),
        ('Хот дотор', 'Хот дотор'),
    ]
    RENT_TYPE = [
        ('', '--------'),
        ('ATM', 'ATM'),
        ('Эмийн сан', 'Эмийн сан'),
        ('Stora Box', 'Stora Box'),
        ('Хөлдүү зайрмаг', 'Хөлдүү зайрмаг'),
        ('Нүдний шилний газар', 'Нүдний шилний газар'),
        ('Others', 'Others'),
    ]
    GENDER = [
        ('', '---------'),
        (True, 'Male'),
        (False, 'Female'),
    ]

    tt_type = f.ChoiceField(choices=TT_TYPE_CHOICES, widget=f.Select(attrs={'class': 'form-control'}), required=False)
    ser_storabox = f.ChoiceField(choices=CONSEQUENCES_CHOICES, widget=f.Select(attrs={'class': 'form-control'}),
                                 required=False)
    ser_Umoney = f.ChoiceField(choices=CONSEQUENCES_CHOICES, widget=f.Select(attrs={'class': 'form-control'}),
                               required=False)
    ser_pow_bank = f.ChoiceField(choices=CONSEQUENCES_CHOICES, widget=f.Select(attrs={'class': 'form-control'}),
                                 required=False)
    ser_lottery = f.ChoiceField(choices=CONSEQUENCES_CHOICES, widget=f.Select(attrs={'class': 'form-control'}),
                                required=False)
    ser_delivery = f.ChoiceField(choices=CONSEQUENCES_CHOICES, widget=f.Select(attrs={'class': 'form-control'}),
                                 required=False)
    ser_print = f.ChoiceField(choices=CONSEQUENCES_CHOICES, widget=f.Select(attrs={'class': 'form-control'}),
                              required=False)
    ser_ticket = f.ChoiceField(choices=CONSEQUENCES_CHOICES, widget=f.Select(attrs={'class': 'form-control'}),
                               required=False)
    toilet_tp = f.ChoiceField(choices=TOILET_TYPE_CHOICES, widget=f.Select(attrs={'class': 'form-control'}),
                              required=False)

    wday_hours = f.TimeField(required=False, input_formats=['%H:%M:%S'],
                             widget=f.TimeInput(attrs={'type': 'time', 'step': '1'})
                             )
    wend_hours = f.TimeField(required=False, input_formats=['%H:%M:%S'],
                             widget=f.TimeInput(attrs={'type': 'time', 'step': '1'})
                             )
    war_yn = f.ChoiceField(choices=CONSEQUENCES_CHOICES, widget=f.Select(attrs={'class': 'form-control'}),
                           required=False)
    squat_toilet_yn = f.ChoiceField(choices=CONSEQUENCES_CHOICES, widget=f.Select(attrs={'class': 'form-control'}),
                                    required=False)
    cu_bar = f.ChoiceField(choices=CONSEQUENCES_CHOICES, widget=f.Select(attrs={'class': 'form-control'}),
                           required=False)
    entrace_connection = f.ChoiceField(choices=CONSEQUENCES_CHOICES, widget=f.Select(attrs={'class': 'form-control'}),
                                       required=False)
    entrance_connection = f.ChoiceField(choices=CONSEQUENCES_CHOICES, widget=f.Select(attrs={'class': 'form-control'}),
                                        required=False)
    alc_lin_tn = f.ChoiceField(choices=CONSEQUENCES_CHOICES, widget=f.Select(attrs={'class': 'form-control'}),
                               required=False)
    alc_type = f.ChoiceField(choices=ALC_TYPE, widget=f.Select(attrs={'class': 'form-control'}), required=False)
    tobbacco_yn = f.ChoiceField(choices=CONSEQUENCES_CHOICES, widget=f.Select(attrs={'class': 'form-control'}),
                                required=False)
    vape_sell = f.ChoiceField(choices=CONSEQUENCES_CHOICES, widget=f.Select(attrs={'class': 'form-control'}),
                              required=False)
    out_city_flow = f.ChoiceField(choices=CONSEQUENCES_CHOICES, widget=f.Select(attrs={'class': 'form-control'}),
                                  required=False)
    in_out_flow = f.ChoiceField(choices=OUT_CITY_FLOW, widget=f.Select(attrs={'class': 'form-control'}), required=False)
    near_bus_station = f.ChoiceField(choices=CONSEQUENCES_CHOICES, widget=f.Select(attrs={'class': 'form-control'}),
                                     required=False)
    sub_rent1 = f.ChoiceField(choices=RENT_TYPE, widget=f.Select(attrs={'class': 'form-control'}), required=False)
    sub_rent2 = f.ChoiceField(choices=RENT_TYPE, widget=f.Select(attrs={'class': 'form-control'}), required=False)
    garbage_area = f.ChoiceField(choices=CONSEQUENCES_CHOICES, widget=f.Select(attrs={'class': 'form-control'}),
                                 required=False)
    water_tank = f.ChoiceField(choices=CONSEQUENCES_CHOICES, widget=f.Select(attrs={'class': 'form-control'}),
                               required=False)
    # sc_sex = f.ChoiceField(choices=GENDER, widget=f.Select(attrs={'class': 'form-control'}),
    #                        required=False)

    # sc_birthdt = f.DateField(input_formats=settings.DATE_INPUT_FORMATS)

    class Meta:
        model = StoreConsultant
        fields = ['sm_num', 'am_num', 'tt_type', 'wday_hours',
                  'wday_hours', 'atm', 'chest_frz_kr', 'chest_frz_ru', 'up_frz_kr', 'up_frz_suu',
                  'up_frz_ice', 'ser_storabox', 'out_city_flow',
                  'ser_Umoney', 'ser_pow_bank', 'ser_lottery', 'ser_delivery', 'ser_print', 'ser_ticket', 'alc_reason',
                  'ciga_reason', 'reason_not_24', 'close_date', 'close_reason', 'near_gs', 'sm_name', 'sm_phone',
                  'prc_grade', 'tv_screen', 'toilet_tp', 'walkin_chiller', 'lunch_case_L8', 'war_yn', 'toilet_seat',
                  'squat_toilet_yn', 'desk_qty', 'chair_qty', 'building_purpose', 'customer_base', 'shelf',
                  'shelf_list', 'entrace_qty',
                  'cu_bar', 'cu_bar_door', 'doorstep_yn', 'doorstep_qty', 'out_banner_qty', 'entrace_connection',
                  'alc_lic_yn', 'tobbacco_yn', 'in_out_flow',
                  'alc_type', 'alc_lin_tn', 'vape_sell', 'car_park_slot',
                  'near_bus_station',
                  'bus_station_range', 'sub_rent1', 'sub_rent2', 'university_range', 'high_school_range',
                  'garbage_area',
                  'garbage_transport', 'water_tank'
                  ]

    class AllocationForm(f.ModelForm):
        tags = f.CharField(widget=f.TextInput(attrs={'class': 'form-control'}), required=False)

        class Meta:
            model = Allocation
            fields = ['consultant', 'area', 'year', 'month', 'team_no', 'store_cons', 'storeID', 'store_name',
                      'tags']


class ConsultantFrom(f.ModelForm):
    class Meta:
        model = Consultants
        fields = ['sc_name', 'sc_surname', 'sc_email', 'sc_phone', 'sc_sex', 'sc_birthdt', 'sc_rel_status',
                  'sc_child', 'sc_Addr1', 'sc_Addr2', 'sc_Addr3', 'sc_Addr4']
