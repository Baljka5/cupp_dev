from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from cupp.point.models import UserPermission


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **kwargs):
        UserPermission.objects.all().delete()

        for user in User.objects.all():
            for perm in user.user_permissions.select_related('content_type').all():
                UserPermission.objects.create(
                    user=user,
                    permission=perm,
                    group=None,
                    codename=perm.codename,
                    name=perm.name,
                    content_type=perm.content_type.model  # from django_content_type
                )

            for group in user.groups.all():
                for perm in group.permissions.select_related('content_type').all():
                    UserPermission.objects.create(
                        user=user,
                        permission=perm,
                        group=group,
                        codename=perm.codename,
                        name=perm.name,
                        content_type=perm.content_type.model
                    )

        self.stdout.write(self.style.SUCCESS('✅ All user permissions with permission details saved.'))
