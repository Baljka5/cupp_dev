from django.shortcuts import render, redirect
from django.http import FileResponse, HttpResponse
from django.conf import settings
from user_agents import parse
import os
import socket
from .models import ZipFile, DownloadedDevice
from .forms import ZipFileForm


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

    user_agent = request.META.get('HTTP_USER_AGENT', '')
    parsed_ua = parse(user_agent)
    os_info = f"{parsed_ua.os.family} {parsed_ua.os.version_string} - {parsed_ua.device.family}"

    client_ip = request.META.get('REMOTE_ADDR', '')

    print(f"device name: {client_ip}")

    try:
        device_name = socket.gethostbyaddr(client_ip)[0]
        print(f"device name: {device_name}")
    except (socket.herror, socket.gaierror):
        device_name = client_ip


    file_path = os.path.join(settings.MEDIA_ROOT, str(zip_file.file))

    success = os.path.exists(file_path)

    # Store download attempt
    DownloadedDevice.objects.create(
        zip_file=zip_file,
        device_name=device_name,  # Now stores PC hostname if available
        os_info=os_info,
        ip_address=client_ip,
        success=success
    )

    if not success:
        return HttpResponse("File not found.", status=404)

    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=zip_file.name)


def downloaded_devices(request):
    devices = DownloadedDevice.objects.select_related('zip_file').all()
    return render(request, 'zip_file/download_devices.html', {'devices': devices})
