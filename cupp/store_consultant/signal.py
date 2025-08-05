from django.db import transaction
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import Consultants
import re

print("signal.py loaded")


def generate_next_sc_code():
    max_number = 0
    consultants = Consultants.objects.exclude(sc_code__isnull=True).exclude(sc_code__exact='')

    for c in consultants:
        match = re.match(r"^SC(\d+)$", c.sc_code.strip())
        if match:
            num = int(match.group(1))
            max_number = max(max_number, num)

    return f"SC{max_number + 1}"


@receiver(post_save, sender='auth.User')
def create_consultant_on_user_create(sender, instance, created, **kwargs):
    """
    Зөвхөн шинэ хэрэглэгч үүсэх үед Consultants бүртгэл автоматаар үүсгэнэ.
    """
    from django.contrib.auth.models import Group

    if not created:
        return  # Зөвхөн шинээр үүсгэх үед ажиллуулна

    if instance.groups.filter(name="Store Consultant").exists():
        with transaction.atomic():
            if not Consultants.objects.filter(sc_email=instance.email).exists():
                sc_code = generate_next_sc_code()
                Consultants.objects.create(
                    sc_name=instance.first_name,
                    sc_surname=instance.last_name,
                    sc_email=instance.email,
                    sc_code=sc_code
                )
                print(f"✅ Consultant created for: {instance.email}")


@receiver(m2m_changed, sender='auth.User_groups')
def handle_user_group_change(sender, instance, action, pk_set, **kwargs):
    """
    Store Consultant group-д хэрэглэгч нэмэгдсэн үед л шинээр Consultants бүртгэнэ
    (Өмнө бүртгэлгүй тохиолдолд).
    """
    if action == "post_add":
        from django.contrib.auth.models import Group
        store_consultant_group = Group.objects.filter(name="Store Consultant").first()

        if store_consultant_group and store_consultant_group.pk in pk_set:
            with transaction.atomic():
                if not Consultants.objects.filter(sc_email=instance.email).exists():
                    sc_code = generate_next_sc_code()
                    Consultants.objects.create(
                        sc_name=instance.first_name,
                        sc_surname=instance.last_name,
                        sc_email=instance.email,
                        sc_code=sc_code
                    )
                    print(f"✅ Consultant created via group assignment for: {instance.email}")
