from django import forms as f
from django.conf import settings

from cupp.common.fields import ClearableFileInput
# from cupp.store_planning.models import StorePlanning

from .models import Point, PointPhoto, StorePlanning
from cupp.constants import CHOICES_POINT_TYPE


class PointForm(f.ModelForm):
    available_date = f.DateField(input_formats=settings.DATE_INPUT_FORMATS)

    # cont_st_dt = f.DateField(input_formats=settings.DATE_INPUT_FORMATS)
    # cont_ed_dt = f.DateField(input_formats=settings.DATE_INPUT_FORMATS)
    # address_det = f.CharField(max_length=500)

    # type = f.ModelChoiceField(queryset=Type.objects.all(), required=True, label='Type', empty_label=None)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(PointForm, self).__init__(*args, **kwargs)

        if not (user and (user.is_superuser or user.groups.filter(name='SP Director').exists())):
            self.fields['type'].choices = [choice for choice in CHOICES_POINT_TYPE if choice[0] != 'CU']

    class Meta:
        model = Point
        fields = ('type', 'lat', 'lon',
                  'owner_name', 'owner_phone', 'owner_email',
                  'base_rent_rate', 'max_rent_rate', 'proposed_layout',
                  'availability', 'available_date', 'size', 'grade',
                  'deposit', 'bep', 'expected_sales', 'passers', 'hh',
                  'office', 'students', 'turnover_rent_percent', 'radius',
                  'isr_file', 'pl_file', 'address', 'store_id', 'store_name'
                  )
        widgets = {
            'proposed_layout': ClearableFileInput(),
            'isr_file': ClearableFileInput(),
            'pl_file': ClearableFileInput(),
        }
        # st_model = StorePlanning
        # st_fields = ('addr1_prov', 'addr2_dist', 'address_det', 'sp_name', 'near_gs_cvs', 'near_school', 'park_slot',
        #              'floor', 'cont_st_dt', 'cont_ed_dt', 'zip_code', 'rent_tp', 'rent_near', 'adv', 'disadv',
        #              'propose',
        #              )


PhotoFormset = f.inlineformset_factory(Point, PointPhoto, fields=['photo'], extra=6)


class StorePlanningForm(f.ModelForm):
    cont_st_dt = f.DateField(input_formats=settings.DATE_INPUT_FORMATS)
    cont_ed_dt = f.DateField(input_formats=settings.DATE_INPUT_FORMATS)

    class Meta:
        model = StorePlanning
        fields = ('__all__')
        # fields = (
        #     'addr1_prov', 'addr2_dist', 'addr3_khr', 'address_det', 'sp_name', 'near_gs_cvs', 'near_school',
        #     'park_slot', 'floor', 'cont_st_dt', 'cont_ed_dt', 'zip_code', 'rent_tp', 'rent_near', 'lessee_promise',
        #     'adv', 'disadv', 'propose',
        # )
