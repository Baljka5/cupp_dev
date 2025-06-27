import os
import uuid

from django.db import models as m
from django.contrib.auth.models import User


class StoreTrainer(m.Model):
    store_id = m.CharField('Store ID', blank=True, null=True, max_length=5)
    store_name = m.CharField('Store name', blank=True, null=True, max_length=500)
    size = m.FloatField('Area size', blank=True, null=True, default=0)
    sitting_size = m.FloatField('Sitting area size', blank=True, null=True, default=0)
    war_size = m.FloatField('Warehouse size', blank=True, null=True, default=0)
    toilet_size = m.FloatField('Toilet size', blank=True, null=True, default=0)
    resale_size = m.FloatField('Hall size', blank=True, null=True, default=0)
    shelf = m.IntegerField('Shelf number', blank=True, null=True, default=0)
    wall_shelf = m.IntegerField('Wall shelf numver', blank=True, null=True, default=0)
    cash_shelf = m.IntegerField('Cash shelf number', blank=True, null=True, default=0)
    st_name = m.CharField('Store trainer name', blank=True, null=True, max_length=50)
    chair_size = m.IntegerField('Chair number', blank=True, null=True, default=0)
    desk_size = m.IntegerField('Desk number', blank=True, null=True, default=0)
    planned_date = m.DateField('Date of plan', blank=True, null=True)
    displayed_date = m.DateField('Displayed date', blank=True, null=True)
    open_date = m.DateField('Opening date', blank=True, null=True)
    open_time = m.TimeField('Opening time', blank=True, null=True)
    light_box = m.IntegerField('Light board number', blank=True, null=True, default=0)
    sand_grill = m.IntegerField('Sandwich grill number', blank=True, null=True, default=0)
    slushie_mach = m.IntegerField('Slushie machine number', blank=True, null=True, default=0)
    icecream_mach = m.IntegerField('Icecream machine', blank=True, null=True, default=0)
    mcs_mach = m.IntegerField('MCS machine', blank=True, null=True, default=0)
    disp_5_mach = m.IntegerField('Zuv aarts machine 5', blank=True, null=True, default=0)
    disp_3_mach = m.IntegerField('Tea machine 3', blank=True, null=True, default=0)
    horizontal_freeze = m.IntegerField('Horizontal freezer', blank=True, null=True, default=0)
    coffee_mach_button = m.IntegerField('Coffee machine number', blank=True, null=True, default=0)
    coffee_mach_led = m.IntegerField('Coffee machine led screen', blank=True, null=True, default=0)
    steamer = m.IntegerField('Steamer number', blank=True, null=True, default=0)
    can_warmer = m.IntegerField('Coffee warmer number', blank=True, null=True, default=0)
    food_warmer = m.IntegerField('Food warmer number', blank=True, null=True, default=0)
    vertical_freezer = m.IntegerField('ISF vertical freezer', blank=True, null=True, default=0)
    dogbuggi_cooker = m.IntegerField('Tteok-bokki machine number', blank=True, null=True, default=0)
    hot_water_disp = m.IntegerField('Water boiler number', blank=True, null=True, default=0)
    tv_screen = m.IntegerField('TV number', blank=True, null=True, default=0)
    pos_qty = m.IntegerField('POS', blank=True, null=True, default=0)
    cam_int = m.IntegerField('Camera', blank=True, null=True, default=0)
    cam_ext = m.IntegerField('External camera', blank=True, default=0)
    monitor_eq = m.CharField('Recording device information', blank=True, null=True, max_length=100)
    hard_disk_size_tb = m.IntegerField('Hard disk size', blank=True, null=True, default=0)
    video_storage_day = m.IntegerField('Days to keep records', blank=True, null=True, default=0)
    is_locked_st = m.BooleanField(default=False, null=True)
    created_date = m.DateTimeField('Created date', auto_now_add=True)
    modified_date = m.DateTimeField('Modified date', auto_now=True)
    created_by = m.ForeignKey(User, verbose_name='Created by', related_name='store_trainer_created',
                              on_delete=m.PROTECT, null=True)
    modified_by = m.ForeignKey(User, verbose_name='Modified by', related_name='store_trainer_modified',
                               on_delete=m.PROTECT, null=True)

    def __str__(self):
        return self.store_id

    def save(self, *args, **kwargs):
        if not self.pk and not self.created_by:
            self.created_by = self.modified_by
        super(StoreTrainer, self).save(*args, **kwargs)

    class Meta:
        db_table = 'store_trainer'
        verbose_name = 'Store Trainer'
