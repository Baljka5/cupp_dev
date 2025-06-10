
from django.db import models
import json

from django.contrib.postgres.fields import JSONField

# class Candidate(models.Model):
#
#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     family_name = models.CharField(max_length=100, blank=True)
#     email = models.EmailField()
#
#     birthday = models.DateField()
#     register_number = models.CharField(max_length=20)
#
#     workplace_code = models.CharField(max_length=20)
#     workplace_name = models.CharField(max_length=100)
#     unit_code = models.CharField(max_length=20)
#     start_date = models.DateField()
#
#     gender = models.CharField(max_length=10)
#     phone_number = models.CharField(max_length=20)
#
#     civil_reg_number = models.CharField(max_length=20, blank=True)
#     bank_account_number = models.CharField(max_length=50, blank=True)
#     bank_name = models.CharField(max_length=100, blank=True)
#
#     address_type1 = models.CharField(max_length=50, blank=True)
#     city1 = models.CharField(max_length=100)
#     district1 = models.CharField(max_length=100)
#     committee1 = models.CharField(max_length=200)
#     address1 = models.CharField(max_length=200)
#
#     address_type2 = models.CharField(max_length=50, blank=True)
#     city2 = models.CharField(max_length=100, blank=True)
#     district2 = models.CharField(max_length=100, blank=True)
#     committee2 = models.CharField(max_length=200, blank=True)
#     address2 = models.CharField(max_length=200, blank=True)
#
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     status = models.CharField(max_length=10, blank=True)
#     employee_id = models.CharField(max_length=50, blank=True),
#     error_message = models.TextField(blank=True),
#     cantidate_id = models.CharField(max_length=50, blank=True),
#
#     def __str__(self):
#         return f"{self.first_name} {self.last_name} ({self.email})"



class PersonalInfoRaw(models.Model):
    data = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, blank=True, default='Pending')
    employee_id = models.CharField(max_length=50, blank=True)
    responseData = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if isinstance(self.data, dict):
            self.data = json.dumps(self.data)
        if isinstance(self.responseData, dict):
            self.responseData = json.dumps(self.responseData)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"PersonalInfoRaw {self.id} - {self.created_at}"