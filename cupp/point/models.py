import os
import uuid
from sqlite3 import IntegrityError

from django.core.exceptions import MultipleObjectsReturned
from django.core.validators import RegexValidator
from django.db import models as m, transaction
from django.contrib.auth.models import User
from django.conf import settings
from uuid import uuid4
from cupp.constants import CHOICES_POINT_TYPE, CHOICES_POINT_GRADE
from cupp.store_trainer.models import StoreTrainer
from cupp.store_consultant.models import StoreConsultant


# from cupp.choices import get_point_type_choices


def upload_file(instance, filename):
    return 'point/%s%s' % (str(uuid.uuid4())[:12], os.path.splitext(filename)[1])


def icon_file(instance, filename):
    return 'static/%s%s' % (str(uuid.uuid4())[:12], os.path.splitext(filename)[1])


class City(m.Model):
    city_code = m.IntegerField('City and aimag code', blank=False, null=True, default=0)
    city_name = m.CharField('City and aimag name', blank=False, default='', max_length=50, unique=True)

    def __str__(self):
        return self.city_name

    class Meta:
        db_table = 'cupp_city'
        verbose_name = 'City'


class District(m.Model):
    district_name = m.CharField('District and sum name', blank=False, default='', max_length=50)
    city = m.ForeignKey(City, on_delete=m.CASCADE, related_name='districts')

    def __str__(self):
        return self.district_name

    class Meta:
        db_table = 'cupp_district'
        verbose_name = 'District'


class Type(m.Model):
    type_name = m.CharField('Type name', blank=False, default='', max_length=50, unique=True)
    type_cd = m.CharField('Type code', blank=False, default='', max_length=50, unique=True)
    icon = m.FileField(upload_to='images/ui')

    # icon = m.FileField(upload_to='static/images/ui/')

    def __str__(self):
        return self.type_name

    class Meta:
        db_table = 'cupp_type'
        verbose_name = 'Type'


# def get_type_choices():
#     return [(type.type_cd, type.type_name) for type in Type.objects.all()]

class Point(m.Model):
    created_date = m.DateTimeField('Created date', auto_now_add=True)
    modified_date = m.DateTimeField('Modified date', auto_now=True)

    created_by = m.ForeignKey(User, verbose_name='Creadted by', related_name='points', on_delete=m.PROTECT)

    # type = m.CharField('Type', max_length=10, choices=get_type_choices())
    store_id = m.CharField('Store ID', blank=True, null=True, max_length=5)
    store_name = m.CharField('Store name', blank=True, null=True, max_length=500)
    type = m.CharField('Type', max_length=10, choices=CHOICES_POINT_TYPE)
    lat = m.CharField('Latitude', max_length=50, default='47.9116')
    lon = m.CharField('Longitude', max_length=50, default='106.9057')

    grade = m.CharField('Location grade', max_length=10, choices=CHOICES_POINT_GRADE, blank=True, null=True,
                        default='A')
    size = m.IntegerField('Size', blank=True, null=True, default=0)
    address = m.CharField('Address', blank=False, default='', max_length=200)

    owner_name = m.CharField('Landlord name', max_length=50, blank=True, null=True)
    owner_phone = m.CharField('Landlord phone', max_length=50, blank=True, null=True)
    owner_email = m.CharField('Landlord email', max_length=50, blank=True, null=True)

    base_rent_rate = m.IntegerField('Base rent', blank=True, null=True, default=0)
    max_rent_rate = m.IntegerField('Maximum rent', blank=True, null=True, default=0)
    turnover_rent_percent = m.IntegerField('Turnover rent percentage', blank=True, null=True, default=0)
    radius = m.IntegerField('Radius by meter /limit 1km/', blank=True, null=True, default=0)
    isr_file = m.FileField('ISR excel file', upload_to=upload_file, blank=True, null=True)
    pl_file = m.FileField('P&L excel file', upload_to=upload_file, blank=True, null=True)

    proposed_layout = m.FileField('Proposed layout', upload_to=upload_file, blank=True, null=True)

    availability = m.BooleanField('Availability', blank=True, null=True)
    available_date = m.DateField('Available date', blank=True, null=True)

    deposit = m.IntegerField('Deposit', blank=True, null=True, default=0)
    bep = m.IntegerField('Breakeven point', blank=True, null=True, default=0)
    expected_sales = m.IntegerField('Expected daily sales', blank=True, null=True, default=0)
    passers = m.IntegerField('Average passers an hour', blank=True, null=True, default=0)
    hh = m.IntegerField('Households in the direct area', blank=True, null=True, default=0)
    office = m.IntegerField('Office people in the direct area', blank=True, null=True, default=0)
    students = m.IntegerField('School/University students in the direct area', blank=True, null=True, default=0)
    # created_by_id = m.ForeignKey(User, verbose_name='Created by', related_name='store_planning_created',
    #                           on_delete=m.PROTECT, null=True)
    modified_by = m.ForeignKey(User, verbose_name='Modified by', related_name='points_modified',
                               on_delete=m.PROTECT, null=True)

    def save(self, *args, **kwargs):

        if not self.pk and not self.created_by:
            self.created_by = self.modified_by
        # super(Point, self).save(*args, **kwargs)
        creating = self._state.adding
        super().save(*args, **kwargs)  # Call the "real" save() method.

        # Create or update the StorePlanning instance
        store_related_defaults = {
            'store_name': self.store_name,
            'store_id': self.store_id,
            'lat': self.lat,
            'lon': self.lon,
            'grade': self.grade,
            'size': self.size,
            'owner_name': self.owner_name,
            'owner_phone': self.owner_phone,
            'owner_email': self.owner_email,
            'base_rent_rate': self.base_rent_rate,
            'proposed_layout': self.proposed_layout,
            'availability': self.availability,
            'deposit': self.deposit,
            'bep': self.bep,
            'expected_sales': self.expected_sales,
            'passers': self.passers,
            'hh': self.hh,
            'office': self.office,
            'students': self.students,
            'available_date': self.available_date,
            'isr_file': self.isr_file,
            'max_rent_rate': self.max_rent_rate,
            'pl_file': self.pl_file,
            'radius': self.radius,
            'turnover_rent_percent': self.turnover_rent_percent,
            'address': self.address,
            'created_by': self.created_by,
            'modified_by': self.modified_by
            # 'cluster': self.cluster,  # Uncomment and modify if cluster exists in Point and needs to be copied
        }
        if creating or not creating:
            try:
                with transaction.atomic():
                    # Update or create StorePlanning instance
                    StorePlanning.objects.update_or_create(
                        store_id=self.store_id,
                        defaults=store_related_defaults
                    )

                    # Update or create StoreTrainer instance
                    StoreTrainer.objects.update_or_create(
                        store_id=self.store_id,
                        defaults={'store_name': self.store_name, 'created_by': self.created_by,
                                  'modified_by_id': self.modified_by}
                    )

                    # Update or create StoreConsultant instance
                    StoreConsultant.objects.update_or_create(
                        store_id=self.store_id,
                        defaults={'store_name': self.store_name, 'created_by': self.created_by,
                                  'modified_by_id': self.modified_by}
                    )
            except MultipleObjectsReturned:

                pass
            except IntegrityError:
                # Handle database integrity errors, such as violations of unique constraints.
                pass

    def __str__(self):
        return '%s - %s' % (self.get_type_display(), self.address)

    class Meta:
        db_table = 'cupp_point'
        verbose_name = 'Point'


class PointPhoto(m.Model):
    point = m.ForeignKey(Point, related_name='photos', on_delete=m.CASCADE)
    photo = m.ImageField(upload_to=upload_file)

    class Meta:
        db_table = 'cupp_point_photo'
        verbose_name = 'Point Photo'


class StorePlanning(m.Model):
    point = m.ForeignKey(Point, on_delete=m.CASCADE, related_name='store_plannings', null=True, blank=True)
    five_digit_validator = RegexValidator(r'^\d{5}$', 'Store number must be a 5-digit number')
    store_id = m.CharField('Store ID', max_length=5, unique=True, blank=True, null=True)
    store_name = m.CharField('Store name', blank=True, null=True, max_length=500)
    lat = m.CharField('Latitude', max_length=50, default='47.9116')
    lon = m.CharField('Longitude', max_length=50, default='106.9057')
    grade = m.CharField('Location grade', max_length=10, choices=CHOICES_POINT_GRADE, blank=True, null=True,
                        default='A')
    size = m.IntegerField('Size', blank=True, null=True, default=0)
    owner_name = m.CharField('Landlord name', max_length=50, blank=True, null=True)
    owner_phone = m.CharField('Landlord phone', max_length=50, blank=True, null=True)
    owner_email = m.CharField('Landlord email', max_length=50, blank=True, null=True)
    base_rent_rate = m.IntegerField('Base rent', blank=True, null=True, default=0)
    proposed_layout = m.FileField('Proposed layout', upload_to=upload_file, blank=True, null=True)
    availability = m.BooleanField('Availability', blank=True, null=True)
    deposit = m.IntegerField('Deposit', blank=True, null=True, default=0)
    bep = m.IntegerField('Breakeven point', blank=True, null=True, default=0)
    expected_sales = m.IntegerField('Expected daily sales', blank=True, null=True, default=0)
    passers = m.IntegerField('Average passers an hour', blank=True, null=True, default=0)
    hh = m.IntegerField('Households in the direct area', blank=True, null=True, default=0)
    office = m.IntegerField('Office people in the direct area', blank=True, null=True, default=0)
    students = m.IntegerField('School/University students in the direct area', blank=True, null=True, default=0)
    available_date = m.DateField('Available date', blank=True, null=True)
    isr_file = m.FileField('ISR excel file', upload_to=upload_file, blank=True, null=True)
    max_rent_rate = m.IntegerField('Maximum rent', blank=True, null=True, default=0)
    pl_file = m.FileField('P&L excel file', upload_to=upload_file, blank=True, null=True)
    radius = m.IntegerField('Radius by meter /limit 1km/', blank=True, null=True, default=0)
    turnover_rent_percent = m.IntegerField('Turnover rent percentage', blank=True, null=True, default=0)
    address = m.CharField('Address', blank=False, default='', max_length=200)
    cluster = m.CharField('Cluster', blank=True, null=True, max_length=500)

    addr1_prov = m.ForeignKey(City, on_delete=m.SET_NULL, null=True, blank=True, verbose_name='City and Aimag')
    addr2_dist = m.ForeignKey(District, on_delete=m.SET_NULL, null=True, blank=True, verbose_name='District and Sum')
    addr3_khr = m.CharField('Хороо', null=True, blank=True, max_length=50)
    address_det = m.CharField('Address detail', blank=True, default='', max_length=500)
    sp_name = m.CharField('SP name', blank=True, default='', max_length=50)
    near_gs_cvs = m.IntegerField('GS25 number', blank=True, null=True, default=0)
    near_school = m.IntegerField('School number', blank=True, null=True, default=0)
    park_slot = m.IntegerField('Park number', blank=True, default=0)
    floor = m.IntegerField('Floor number', blank=True, default=0)
    cont_st_dt = m.DateField('Rent agreement start date', blank=True, null=True)
    cont_ed_dt = m.DateField('Rent agreement end date', blank=True, null=True)
    zip_code = m.CharField('Zip code', blank=True, default='', max_length=100)
    rent_tp = m.BooleanField('Type of rent agreement', blank=True, null=True)
    rent_near = m.CharField('Company name', blank=True, default='', max_length=50)
    lessee_promise = m.CharField('Амлалт', blank=True, null=True, max_length=50)
    adv = m.TextField('Advantage', blank=True, default='')
    disadv = m.TextField('Disadvantage', blank=True, default='')
    propose = m.TextField('Suggestions for improvement', blank=True, null=True)
    address_simple = m.CharField('Address Simple', blank=True, null=True, max_length=255)
    storeEmail = m.CharField('Store email', blank=True, null=True, max_length=50)
    created_date = m.DateTimeField('Created date', auto_now_add=True)
    modified_date = m.DateTimeField('Modified date', auto_now=True)
    created_by = m.ForeignKey(User, verbose_name='Created by', related_name='store_planning_created',
                              on_delete=m.PROTECT, null=True)
    modified_by = m.ForeignKey(User, verbose_name='Modified by', related_name='store_planning_modified',
                               on_delete=m.PROTECT, null=True)

    # class TeamManager(m.Model):

    def __str__(self):
        return self.store_id

    def save(self, *args, **kwargs):
        if not self.pk and not self.created_by:
            self.created_by = self.modified_by
        super(StorePlanning, self).save(*args, **kwargs)

    class Meta:
        db_table = 'store_planning'
        verbose_name = 'Store Planning'
