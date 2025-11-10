from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
import json

from django.conf import settings
from .forms import MainTableForm
from .models import MainTable, DimensionTable
from .models import WhistleBlow
from django.template.loader import render_to_string

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import generic as g


def addnew(request):
    lic_id_to_name = {dimension.lic_id: dimension.lic_id_nm for dimension in DimensionTable.objects.all()}
    if request.method == "POST":
        form = MainTableForm(request.POST, request.FILES)
        print(request.FILES)
        if form.is_valid():
            try:
                form.instance.created_by = request.user if not form.instance.pk else form.instance.created_by
                form.instance.modified_by = request.user
                form.save()
                messages.success(request, 'Form submission successful.')
                return redirect('/register-license')
            except Exception as e:
                # If save fails, add an error message and print the exception
                messages.error(request, 'Form could not be saved. Please try again.')
                print(f"Error saving form: {e}")
        else:
            # If form is not valid, show errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
    else:
        form = MainTableForm()

    return render(request, 'license/test_form.html', {
        'form': form,
        'lic_id_to_name': lic_id_to_name,
    })


# def index(request):
#     models = MainTable.objects.all()
#     return render(request, "license/show.html", {'models': models})

def index(request):
    # Retrieve filter values from GET request
    store_id_query = request.GET.get('store_id', '')
    lic_id_nm_query = request.GET.get('lic_id_nm', '')

    # Build the query based on presence of filter values
    query = Q()
    if store_id_query:
        query &= Q(store_id__icontains=store_id_query)
    if lic_id_nm_query:
        query &= Q(lic_id__lic_id_nm__icontains=lic_id_nm_query)

    models = MainTable.objects.filter(query).distinct().order_by('-store_id')

    paginator = Paginator(models, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "license/show.html", {
        'page_obj': page_obj,
        'store_id_query': store_id_query,
        'lic_id_nm_query': lic_id_nm_query
    })

def lic_show(request, id):
    model = MainTable.objects.get(id=id)
    return render(request, 'license/lic_show.html', {
        'model': model
    })

def edit(request, id):
    model = MainTable.objects.get(id=id)
    types = DimensionTable.objects.all()
    return render(request, 'license/edit.html', {'model': model, 'types': types})


def update(request, id):
    model = MainTable.objects.get(id=id)
    types = DimensionTable.objects.all()
    form = MainTableForm(request.POST, instance=model)
    if form.is_valid():
        form.save()
        return redirect("/register-license")
    return render(request, 'license/edit.html', {'model': model, 'types': types})


def destroy(request, id):
    model = MainTable.objects.get(id=id)
    model.delete()
    return redirect("/register-license")

def whistle(request):
    # model = MainTable.objects.get(id=id)
    # model.delete()
    return render(request, 'license/blow-whistle.html', {})

def whistle_submit(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        # request.body нь bytes → decode → json.loads
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError as e:
        return JsonResponse({'error': 'Invalid JSON', 'detail': str(e)}, status=400)
    print(data)
    # JSON-аас утгуудыг авах
    wh_d = {}
    wh_d['harm_type'] = data.get('harm_type')
    wh_d['damage_causer'] = data.get('damage_causer')
    wh_d['damage_desc'] = data.get('damage_desc')
    wh_d['damage_photo'] = data.get('damage_photo')  # FILE upload биш бол file path-ийг text-р хадгалж болно
    wh_d['blower_firstName'] = data.get('blower_firstName')
    wh_d['blower_lastName'] = data.get('blower_lastName')
    wh_d['blower_company'] = data.get('blower_company')
    wh_d['blower_position'] = data.get('blower_position')
    wh_d['blower_phone'] = data.get('blower_phone')
    wh_d['blower_email'] = data.get('blower_email')
    wh_d['blower_secret'] = data.get('blower_secret') in ['1', 'true', True]  # boolean рүү хөрвүүлэх
    wh_d['blower_messenger'] = data.get('blower_messenger')
    wh_d['blower_messenger_name'] = data.get('blower_messenger_name')


    # Model-д хадгалах
    whistle = WhistleBlow.objects.create(
        harm_type = wh_d['harm_type'],
        damage_causer = wh_d['damage_causer'],
        damage_desc = wh_d['damage_desc'],
        damage_photo = wh_d['damage_photo'],
        blower_firstName = wh_d['blower_firstName'],
        blower_lastName = wh_d['blower_lastName'],
        blower_company = wh_d['blower_company'],
        blower_position = wh_d['blower_position'],
        blower_phone = wh_d['blower_phone'],
        blower_email = wh_d['blower_email'],
        blower_secret = wh_d['blower_secret'],
        blower_messenger = wh_d['blower_messenger'],
        blower_messenger_name = wh_d['blower_messenger_name']
    )
    # send_whistle_mail(wh_d)
    return JsonResponse({'success': True, 'id': wh_d})

def send_whistle_mail(request):


    # print(request)
    to_emails = ["enkhsaikhan.e@cumongol.mn"]
    cc_emails = ["enkhsaikhan.e@cumongol.mn"]
    try:
        # 1️⃣ HTML template-д ашиглах өгөгдлөө бэлдэх
        context = {
            "harm_type": request.get("harm_type"),
            "damage_causer": request.get("damage_causer"),
            "damage_desc": request.get("damage_desc"),
            "blower_firstName": request.get("blower_firstName"),
            "blower_lastName": request.get("blower_lastName"),
            "blower_photo": request.get("blower_photo"),
            "blower_company": request.get("blower_company"),
            "blower_position": request.get("blower_position"),
            "blower_phone": request.get("blower_phone"),
            "blower_email": request.get("blower_email"),
            "blower_secret": request.get("blower_secret"),
            "blower_messenger": request.get("blower_messenger"),
            "blower_messenger_name": request.get("blower_messenger_name"),
        }

        # Template-ээ render хийх
        html_content = render_to_string("license/blow_email_template.html", context)

        # Имэйл мессеж үүсгэх
        msg = MIMEMultipart("alternative")
        msg["From"] = settings.DEFAULT_FROM_EMAIL
        msg["To"] = ", ".join(to_emails)
        msg["Cc"] = ", ".join(cc_emails)
        msg["Subject"] = settings.DEFAULT_FROM_EMAIL + " - Whistle Blower Notification"

        # HTML хувилбарыг хавсаргах
        msg.attach(MIMEText(html_content, "html"))

        all_recipients = to_emails + cc_emails

        # SMTP серверээр илгээх
        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            server.starttls()
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.sendmail(settings.DEFAULT_FROM_EMAIL, all_recipients, msg.as_string())

        print("HTML имэйл амжилттай илгээгдлээ.")
    except Exception as e:
        print(f"Failed to send email: {e}")
    return JsonResponse({'success': True, 'id': request})

class LicenseView(g.TemplateView):
    template_name = 'base.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the is_event_member variable
        context['is_event_member'] = self.request.user.groups.filter(name='license').exists()
        return context
