from django import forms as f
from django.conf import settings
from cupp.store_consultant.models import StoreConsultant, Allocation, Tag


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
        ('Stora box', 'Stora box'),
        ('Хөлдүү зайрмаг', 'Хөлдүү зайрмаг'),
        ('Нүдний шилний газар', 'Нүдний шилний газар'),
        ('Other', 'Other'),
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
    doorstep_yn = f.ChoiceField(choices=CONSEQUENCES_CHOICES, widget=f.Select(attrs={'class': 'form-control'}),
                                required=False)
    entrance_connection = f.ChoiceField(choices=CONSEQUENCES_CHOICES, widget=f.Select(attrs={'class': 'form-control'}),
                                        required=False)
    alc_lin_tn = f.ChoiceField(choices=CONSEQUENCES_CHOICES, widget=f.Select(attrs={'class': 'form-control'}),
                               required=False)
    alc_type = f.ChoiceField(choices=ALC_TYPE, widget=f.Select(attrs={'class': 'form-control'}), required=False)
    tobacco_yn = f.ChoiceField(choices=CONSEQUENCES_CHOICES, widget=f.Select(attrs={'class': 'form-control'}),
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
    sc_sex = f.ChoiceField(choices=GENDER, widget=f.Select(attrs={'class': 'form-control'}),
                           required=False)

    class Meta:
        model = StoreConsultant
        fields = "__all__"

    class AllocationForm(f.ModelForm):
        tags = f.CharField(widget=f.TextInput(attrs={'class': 'form-control'}), required=False)

        class Meta:
            model = Allocation
            fields = ['consultant', 'area', 'year', 'month', 'team_no', 'store_cons', 'storeID', 'store_name',
                      'tags']
