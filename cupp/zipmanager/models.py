from django.db import models


# Create your models here.
class ZipFile(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='zips/')
    upload_date = models.DateTimeField(auto_now_add=True)
    version = models.CharField(max_length=20)
    download_count = models.IntegerField(default=0)
    is_download = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.version} (Downloadable: {self.is_download})"
