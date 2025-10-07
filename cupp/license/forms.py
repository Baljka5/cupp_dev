from django import forms as f
from django.conf import settings
from .models import MainTable
from cupp.point.models import District, City
from cupp.event.models import ActionOwner
from cupp.common.fields import ClearableFileInput


class MainTableForm(f.ModelForm):
    st_dt = f.DateField(input_formats=settings.DATE_INPUT_FORMATS)
    ed_dt = f.DateField(input_formats=settings.DATE_INPUT_FORMATS)

    # alc_type = f.ChoiceField(choices=[('', '---------'), ('high', 'High'), ('low', 'Low'), ('both', 'Both')],
    #                          widget=f.Select(attrs={'class': 'form-control'}))
    # lic_type = f.ChoiceField(choices=[('', '---------'), ('24H', '24H'), ('17H', '17H')],
    #                          widget=f.Select(attrs={'class': 'form-control'}))
    # link_path = f.URLField(widget=f.URLInput(attrs={'class': 'form-control'}))
    link_path = f.URLField(required=False, widget=f.URLInput(attrs={'class': 'form-control'}))
    # lic_duration = f.IntegerField(widget=f.NumberInput(attrs={'class': 'form-control'}))

    # alc_opentime = f.TimeField(input_formats=settings.TIME_INPUT_FORMATS)
    # alc_closetime = f.TimeField(input_formats=settings.TIME_INPUT_FORMATS)

    class Meta:
        model = MainTable
        fields = ['store_id', 'lic_id', 'lic_id_nm', 'lic_yn', 'st_dt', 'ed_dt', 'lic_owner', 'lic_prov_ID',
                  'lic_prov_name', 'lic_no', 'alc_opentime', 'alc_closetime', 'camera_cnt', 'lic_sqrm', 'alc_type',
                  'lic_type', 'link_path', 'lic_status', 'lic_duration','lic_file']
        widgets = {'store_id': f.TextInput(attrs={'class': 'form-control'}),
                   'lic_id_nm': f.TextInput(attrs={'class': 'form-control'}),
                   'lic_owner': f.TextInput(attrs={'class': 'form-control'}),
                   'lic_prov_ID': f.TextInput(attrs={'class': 'form-control'}),
                   'lic_prov_name': f.TextInput(attrs={'class': 'form-control'}),
                   'lic_no': f.TextInput(attrs={'class': 'form-control'}),
                   }


