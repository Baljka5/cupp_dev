import os
import uuid

from django.db import models as m
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# from django.db.models import JSONField


class StoreConsultant(m.Model):
    store_id = m.CharField('Store ID', blank=True, null=True, max_length=5)
    store_name = m.CharField('Store Name', blank=True, null=True, max_length=50)
    store_type = m.IntegerField('store type', default=0)
    team_mgr = m.CharField('Team manager name', blank=True, null=True, max_length=50)
    sc_name = m.CharField('Store consultant name', blank=True, null=True, max_length=50)
    sm_num = m.IntegerField('Дэлгүүрийн менежерийн тоо', blank=True, null=True)
    am_num = m.IntegerField('Дэлгүүрийн туслах менежерийн тоо', blank=True, null=True)
    tt_type = m.CharField('Working timetable', blank=True, null=True, max_length=50)
    wday_hours = m.CharField('Timetable', blank=True, null=True, max_length=50)
    wend_hours = m.CharField('Timetable', blank=True, null=True, max_length=50)
    atm = m.IntegerField('ATM number', blank=True, null=True, default=0)
    chest_frz_ru = m.IntegerField('Horizontal freezer /Russian, Mongolia/', blank=True, null=True, default=0)
    chest_frz_kr = m.IntegerField('Horizontal freezer /Korea/', blank=True, null=True, default=0)
    up_frz_kr = m.IntegerField('Vertical freezer /Korea', blank=True, null=True, default=0)
    ba_rob_frz = m.IntegerField('Baskin robbins freezer', blank=True, null=True, default=0)
    up_frz_suu = m.IntegerField('Horizontal milk freezer', blank=True, null=True, default=0)
    up_frz_ice = m.IntegerField('Horizontal icemark freezer', blank=True, null=True)
    ser_storabox = m.BooleanField('Stora Box', blank=True, null=True)
    ser_Umoney = m.BooleanField('Автобусны карт цэнэглэгчтэй эсэх', blank=True, null=True)
    ser_pow_bank = m.BooleanField('Зөөврийн цэнэглэгч түрээс', blank=True, null=True)
    ser_lottery = m.BooleanField('Сугалаа', blank=True, null=True)
    ser_delivery = m.BooleanField('Хүргэлт', blank=True, null=True)
    ser_print = m.BooleanField('Хэвлэл', blank=True, null=True)
    ser_ticket = m.BooleanField('Тасалбар', blank=True, null=True)
    alc_reason = m.TextField('Reason for not having alcohol license', blank=True, null=True)
    ciga_reason = m.TextField('Reason for not having cigar license', blank=True, null=True)
    reason_not_24 = m.TextField('Reason for not having 24 hour working', blank=True, null=True)
    close_date = m.DateField('Closing date', blank=True, null=True)
    close_reason = m.TextField('Reason for closing store', blank=True, null=True)
    near_gs = m.CharField('GS detail status', blank=True, null=True, max_length=100)
    sm_name = m.CharField('Store manager name', blank=True, null=True, max_length=50)
    sm_phone = m.IntegerField('Store manager phone', blank=True, null=True, default=0)
    prc_grade = m.CharField('Pricing policy', blank=True, null=True, max_length=50)
    tv_screen = m.IntegerField('Tv screen', blank=True, null=True)
    toilet_tp = m.BooleanField('00-н төрөл (Өөрийн, нийтийн)', blank=True, null=True)
    walkin_chiller = m.IntegerField('Уух ус ундааны босоо хөргүүрийн хаалганы тоо', blank=True, null=True, default=0)
    lunch_case_L8 = m.IntegerField('Хоолны хөргүүрийн тоо ', blank=True, null=True, default=0)

    war_yn = m.BooleanField('Дэлгүүр агуулахтай эсэх', blank=True, null=True)
    toilet_seat = m.IntegerField('Суултуурын тоо', blank=True, null=True, default=0)
    squat_toilet_yn = m.BooleanField('Дэлгүүрийн гадна модон 00 той эсэх', blank=True, null=True)
    desk_qty = m.IntegerField('Суух хэсэгтэй бол хэдэн ширээ байгаа вэ?', blank=True, null=True, default=0)
    chair_qty = m.IntegerField('Суух хэсэгтэй бол хэдэн сандал байгаа вэ?', blank=True, null=True, default=0)
    building_purpose = m.CharField('Дэлгүүр байршдаг барилга ямар зориулалттай вэ?', blank=True, null=True,
                                   max_length=255)
    customer_base = m.IntegerField('Объектийн ажилтан, оршин суугчийн тоо', blank=True, null=True, default=0)
    shelf = m.IntegerField('Дэлгүүрийн лагууны тоо', blank=True, null=True, default=0)
    shelf_list = m.IntegerField('Дэлгүүрийн тавцангийн тоо', blank=True, null=True, default=0)
    entrace_qty = m.IntegerField('Дэлгүүр хэдэн орж гарах гарц/үүд-тэй вэ?', blank=True, null=True, default=0)
    cu_bar = m.BooleanField('CU BAR-тай эсэх', blank=True, null=True)
    cu_bar_door = m.IntegerField('CU BAR тоо /Хаалга/', blank=True, null=True, default=0)
    doorstep_yn = m.BooleanField('Дэлгүүрийн үүд шаттай эсэх', blank=True, null=True)
    doorstep_qty = m.IntegerField('Гадна шатны тоо', blank=True, null=True, default=0)
    out_banner_qty = m.IntegerField('Гадна хаягны тоо', blank=True, null=True, default=0)
    entrace_connection = m.BooleanField('Орцруу холбогддог эсэх', blank=True, null=True)
    alc_lic_yn = m.BooleanField('Архины зөвшөөрөлтэй эсэх', blank=True, null=True)
    alc_type = m.BooleanField('Архины зөвшөөрөлтэй бол сул, эсвэл чанга аль нь вэ?', blank=True, null=True)
    tobbacco_yn = m.BooleanField('Утаат тамхины зөвшөөрөлтэй эсэх', blank=True, null=True)
    vape_sell = m.BooleanField('Электрон тамхи зарж буй эсэх', blank=True, null=True)
    out_city_flow = m.BooleanField('Хотоос гарах урсгал эсэх', blank=True, null=True)
    in_out_flow = m.CharField('Хотоос гарах урсгалын салбар бол аль талд нь байрлалтай вэ?', blank=True, null=True,
                              max_length=50)
    car_park_slot = m.IntegerField('Машины зогсоолтой бол хичнээн машин багтах боломжтой вэ?', blank=True, null=True,
                                   default=0)
    near_bus_station = m.BooleanField('Автобусны буудалтай ойр байршдаг уу?', blank=True, null=True)
    bus_station_range = m.FloatField('Автобусны буудлын зай', blank=True, null=True, default=0)
    sub_rent1 = m.CharField('Дамжуулдаг түрээсэлдэг төрөл', blank=True, null=True, max_length=50)
    sub_rent2 = m.CharField('Дамжуулдаг түрээсэлдэг төрөл', blank=True, null=True, max_length=50)
    university_range = m.IntegerField('Урсгалд нөлөөлдөг их суруультай эсэх, зай?', blank=True, null=True, default=0)
    high_school_range = m.FloatField('Урсгалд нөлөөлдөг дунд сургуультай эсэх, зай?', blank=True, null=True, default=0)
    garbage_area = m.BooleanField('Тусдаа хогийн цэгтэй эсэх', blank=True, null=True)
    garbage_transport = m.IntegerField('Хогоо сардаа хэд ачуулдаг вэ?', blank=True, null=True, default=0)
    water_tank = m.BooleanField('Зөөврийн устай эсэх', blank=True, null=True)

    use_yn = m.BooleanField('Use yn', blank=True, null=True, default=0)

    created_date = m.DateTimeField('Created date', auto_now_add=True, null=True)
    modified_date = m.DateTimeField('Modified date', auto_now=True, null=True)
    created_by = m.ForeignKey(User, verbose_name='Created by', related_name='store_consultant_created',
                              on_delete=m.PROTECT, null=True, blank=True)
    modified_by = m.ForeignKey(User, verbose_name='Modified by', related_name='store_consultant_modified',
                               on_delete=m.PROTECT, null=True, blank=True)

    def __str__(self):
        return self.store_id

    def save(self, *args, **kwargs):
        if not self.pk and not self.created_by:
            self.created_by = self.modified_by
        super(StoreConsultant, self).save(*args, **kwargs)

    class Meta:
        db_table = 'store_consultant'
        verbose_name = 'Store Consultant'


class Area(m.Model):
    team_no = m.CharField('Area No', max_length=10, blank=True, null=True)
    team_man_name = m.CharField('Area manager name', max_length=50, blank=True, null=True)
    team_man_surname = m.CharField('Area manager surname', max_length=50, blank=True, null=True)
    team_man_email = m.EmailField('Area manager email address', blank=True, null=True)
    team_man_phone = m.IntegerField('Area manager phone number', blank=True, null=True, default=0)
    team_man_sex = m.BooleanField('Area manager gender', blank=True, null=True)
    team_man_birthdt = m.DateField('Area manager birthday', blank=True, null=True)
    team_man_rel_status = m.BooleanField('Area manager marital status', blank=True, null=True)
    team_man_child = m.IntegerField('Area manager number of children', blank=True, null=True, default=0)
    team_man_Addr1 = m.CharField('Living city', blank=True, null=True, max_length=50)
    team_man_Addr2 = m.CharField('Living district', blank=True, null=True, max_length=50)
    team_man_Addr3 = m.CharField('Living khoroo', blank=True, null=True, max_length=50)
    team_man_Addr4 = m.CharField('Address detail', blank=True, null=True, max_length=50)
    created_date = m.DateTimeField('Created date', auto_now_add=True)
    created_by = m.ForeignKey(User, verbose_name='Created by', related_name='area_manager_created', on_delete=m.PROTECT,
                              null=True)
    modified_date = m.DateTimeField('Modified date', auto_now=True)
    modified_by = m.ForeignKey(User, verbose_name='Modified by', related_name='area_manager_modified',
                               on_delete=m.PROTECT,
                               null=True)

    def __str__(self):
        return '%s - %s' % (self.team_no, self.team_man_name)

    def save(self, *args, **kwargs):
        if not self.pk and not self.created_by:
            self.created_by = self.modified_by
        super(Area, self).save(*args, **kwargs)

    class Meta:
        db_table = 'area_manager'
        verbose_name = 'Area Manger'


class Consultants(m.Model):
    sc_name = m.CharField('Store name of consultants', max_length=50, blank=True, null=True)
    sc_surname = m.CharField('Surname of store consultants', max_length=50, blank=True, null=True)
    sc_email = m.EmailField('Email address of store consultants', blank=True, null=True)
    sc_phone = m.IntegerField('Phone number of store consultants', blank=True, null=True)
    sc_sex = m.BooleanField('Gender of store consultant', blank=True, null=True)
    sc_birthdt = m.DateField('Birth date of store consultant', blank=True, null=True)
    sc_rel_status = m.BooleanField('Relation status of store consultant', blank=True, null=True)
    sc_child = m.IntegerField('Child number of store consultant', blank=True, null=True)
    sc_Addr1 = m.CharField('Living city', blank=True, null=True, max_length=50)
    sc_Addr2 = m.CharField('Living district', blank=True, null=True, max_length=50)
    sc_Addr3 = m.CharField('Living khoroo', blank=True, null=True, max_length=50)
    sc_Addr4 = m.CharField('Detail address', blank=True, null=True, max_length=50)
    created_date = m.DateTimeField('Created date', auto_now_add=True)
    created_by = m.ForeignKey(User, verbose_name='Created by', related_name='sc_created', on_delete=m.PROTECT,
                              null=True)
    modified_date = m.DateTimeField('Modified date', auto_now=True)
    modified_by = m.ForeignKey(User, verbose_name='Modified by', related_name='sc_modified',
                               on_delete=m.PROTECT,
                               null=True)

    def __str__(self):
        return self.sc_name

    def save(self, *args, **kwargs):
        if not self.pk and not self.created_by:
            self.created_by = self.modified_by
        super(Consultants, self).save(*args, **kwargs)

    class Meta:
        db_table = 'consultant'
        verbose_name = 'Consultant'


class Tag(m.Model):
    name = m.CharField(max_length=50)
    consultants = m.ManyToManyField(Consultants, related_name="tags")

    def __str__(self):
        return self.name


class SC_Store_Allocation(m.Model):
    consultant = m.ForeignKey(Consultants, on_delete=m.CASCADE, related_name='store_allocations')
    store = m.ForeignKey(StoreConsultant, on_delete=m.CASCADE, related_name='sc_allocations')
    store_name = m.CharField(max_length=100)
    sc_name = m.CharField(max_length=100, null=True, blank=True)  # Add this field to store the consultant's name
    store_no = m.CharField(max_length=5, null=True, blank=True)
    created_date = m.DateTimeField(auto_now_add=True)
    modified_date = m.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sc_store_allocation'
        verbose_name = 'SC Store Allocation'
        verbose_name_plural = 'SC Store Allocations'

    def __str__(self):
        return f"{self.consultant.sc_name} - {self.store.store_id} ({self.store_name})"


# @receiver(post_save, sender=SC_Store_Allocation)
# def sync_allocation(sender, instance, created, **kwargs):
#     """
#     Sync SC_Store_Allocation with Allocation table.
#     """
#     # Get or create an allocation record for the given store and consultant
#     allocation, allocation_created = Allocation.objects.update_or_create(
#         storeID=instance.store_no,  # Match the storeID field
#         defaults={
#             'store_name': instance.store_name,
#             'store_cons': instance.sc_name,
#             'consultant': instance.consultant,  # Link the consultant directly
#         }
#     )
#     # Save the allocation record
#     allocation.save()


class Allocation(m.Model):
    consultant = m.ForeignKey(Consultants, on_delete=m.CASCADE, null=True, blank=True)
    area = m.ForeignKey(Area, on_delete=m.SET_NULL, null=True, blank=True)
    year = m.CharField('Year', max_length=4, blank=True, null=True)
    month = m.CharField('Month', max_length=12, blank=True, null=True)
    team_no = m.CharField('Team No', max_length=10, blank=True, null=True)
    store_cons = m.CharField('Store Consultant', max_length=50, blank=True, null=True)
    storeID = m.CharField('Store ID', max_length=5, blank=True, null=True)
    store_name = m.CharField('Store Name', max_length=50, blank=True, null=True)
    tags = m.TextField('Tags and Store IDs', blank=True, null=True)
    created_date = m.DateTimeField('Created date', auto_now_add=True)
    created_by = m.ForeignKey(User, verbose_name='Created by', related_name='allocation_created', on_delete=m.PROTECT,
                              null=True)
    modified_date = m.DateTimeField('Modified date', auto_now=True)
    modified_by = m.ForeignKey(User, verbose_name='Modified by', related_name='allocation_modified',
                               on_delete=m.PROTECT,
                               null=True)

    def __str__(self):
        return self.team_no

    def save(self, *args, **kwargs):
        if not self.pk and not self.created_by:
            self.created_by = self.modified_by
        super(Allocation, self).save(*args, **kwargs)

    class Meta:
        db_table = 'allocation'
        verbose_name = 'Allocation'


class HisAllocation(m.Model):
    # Fields from SC_Store_Allocation
    consultant = m.ForeignKey(Consultants, on_delete=m.CASCADE, related_name='his_store_allocations')
    store = m.ForeignKey(StoreConsultant, on_delete=m.CASCADE, related_name='his_sc_allocations')
    store_name = m.CharField(max_length=100, blank=True, null=True)  # From SC_Store_Allocation
    sc_name = m.CharField(max_length=100, blank=True, null=True)  # From SC_Store_Allocation
    store_no = m.CharField(max_length=5, blank=True, null=True)  # From SC_Store_Allocation
    year = m.CharField('Year', max_length=4, blank=True, null=True)  # From Allocation
    month = m.CharField('Month', max_length=12, blank=True, null=True)  # From Allocation
    team_no = m.CharField('Team No', max_length=10, blank=True, null=True)  # From Allocation
    area = m.ForeignKey(Area, on_delete=m.SET_NULL, null=True, blank=True)
    store_cons = m.CharField('Store Consultant', max_length=50, blank=True, null=True)
    tags = m.TextField('Tags and Store IDs', blank=True, null=True)
    created_date = m.DateTimeField(auto_now_add=True)
    modified_date = m.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.store_no} - {self.consultant.sc_name} (Historical Record)"

    class Meta:
        db_table = 'his_allocation'
        verbose_name = 'Historical Allocation'
        verbose_name_plural = 'Historical Allocations'
