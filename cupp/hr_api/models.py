from django.db import models
import json

from django.db import models
import json
from django.utils import timezone


class PersonalInfoRaw(models.Model):
    unique_id = models.CharField(max_length=50, blank=True)
    data = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, blank=True, default='PENDING')
    employee_id = models.CharField(max_length=50, blank=True, null=True)
    responseData = models.TextField(blank=True, null=True)
    old_json = models.TextField(blank=True, null=True)
    new_json = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # JSON encode without escaping Unicode
        if isinstance(self.data, dict):
            self.data = json.dumps(self.data, ensure_ascii=False)

        if isinstance(self.responseData, dict):
            self.responseData = json.dumps(self.responseData, ensure_ascii=False)

        # Old/new JSON tracking
        if self.pk:
            try:
                old_instance = PersonalInfoRaw.objects.get(pk=self.pk)
                if old_instance.data != self.data:
                    self.old_json = old_instance.data
                    self.new_json = self.data
                    self.updated_at = timezone.now()
            except PersonalInfoRaw.DoesNotExist:
                pass  # skip on first creation

        # Auto status update from responseData
        try:
            response = json.loads(self.responseData or "{}")
            if isinstance(response, dict) and "status" in response:
                self.status = response.get("status", self.status)
        except Exception:
            pass

        super().save(*args, **kwargs)

    def __str__(self):
        return f"PersonalInfoRaw {self.id} - {self.created_at}"


class EmpPersonalInfoRaw(models.Model):
    data = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, blank=True, default='PENDING')
    employee_id = models.CharField(max_length=50, blank=True)
    responseData = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if isinstance(self.data, dict):
            self.data = json.dumps(self.data)

        if isinstance(self.responseData, dict):
            self.responseData = json.dumps(self.responseData)

        try:
            response = json.loads(self.responseData or "{}")
            if isinstance(response, dict) and "status" in response:
                self.status = response.get("status", self.status)
        except Exception:
            pass

        super().save(*args, **kwargs)

    def __str__(self):
        return f"PersonalInfoRaw {self.id} - {self.created_at}"
