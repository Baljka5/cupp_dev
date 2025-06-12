
from django.db import models
import json


class PersonalInfoRaw(models.Model):
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