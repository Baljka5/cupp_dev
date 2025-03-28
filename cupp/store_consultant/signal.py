from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import Consultants

print("✅ signal.py loaded")


@receiver(post_save, sender='auth.User')  # <-- string ашиглаж delayed load хийх
def create_or_update_consultant_if_in_group(sender, instance, **kwargs):
    from django.contrib.auth.models import Group  # <-- import дотогш нь оруул
    if instance.groups.filter(name="Store Consultant").exists():
        obj, created = Consultants.objects.update_or_create(
            sc_email=instance.email,
            defaults={
                'sc_name': instance.first_name,
                'sc_surname': instance.last_name,
                'sc_email': instance.email
            }
        )
        action = "created" if created else "updated"
        print(f"🚀 Consultant {action} for: {instance.email}")


@receiver(m2m_changed, sender='auth.User_groups')  # <-- string again
def handle_user_group_change(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        from django.contrib.auth.models import Group  # <-- import дотогш нь оруул
        store_consultant_group = Group.objects.filter(name="Store Consultant").first()
        if store_consultant_group and store_consultant_group.pk in pk_set:
            obj, created = Consultants.objects.update_or_create(
                sc_email=instance.email,
                defaults={
                    'sc_name': instance.first_name,
                    'sc_surname': instance.last_name,
                    'sc_email': instance.email
                }
            )
            action = "created" if created else "updated"
            print(f"⚡ Consultant {action} via group assignment: {instance.email}")
