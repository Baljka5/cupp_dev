from django.shortcuts import render, get_object_or_404, redirect
from django.http import FileResponse, HttpResponse
from django.conf import settings
import os
from .models import ZipFile
from .forms import ZipFileForm


# Create your views here.

def upload_zip(request):
    if request.method == 'POST':
        form = ZipFileForm(request.POST, request.FILES)
        if form.is_valid():
            ZipFile.objects.update(is_download=False)

            zip_instance = form.save(commit=False)
            zip_instance.name = request.FILES['file'].name
            zip_instance.is_download = True
            zip_instance.save()

            return redirect('zip_list')

    else:
        form = ZipFileForm()
    return render(request, 'zip_file/upload.html', {'form': form})


def zip_list(request):
    files = ZipFile.objects.all()
    return render(request, 'zip_file/zip_list.html', {'files': files})


def download_latest_zip(request):
    zip_file = ZipFile.objects.filter(is_download=True).order_by('-upload_date').first()
    if not zip_file:
        return HttpResponse("No files available for download.", status=404)

    zip_file.download_count += 1
    zip_file.save()

    file_path = os.path.join(settings.MEDIA_ROOT, str(zip_file.file))
    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=zip_file.name)
