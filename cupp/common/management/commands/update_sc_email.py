from django.core.management.base import BaseCommand
from cupp.store_consultant.models import StoreConsultant, SC_Store_Allocation, Consultants, Allocation, Area
from django.db import transaction


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **kwargs):
        updated_count = 0

        with transaction.atomic():
            for store in StoreConsultant.objects.all():
                allocation = SC_Store_Allocation.objects.filter(store_no=store.store_id).first()
                if allocation and allocation.sc_name:
                    consultant = Consultants.objects.filter(sc_name=allocation.sc_name).first()
                    if consultant and consultant.sc_email:
                        store.sc_name = consultant.sc_email

                        team_allocation = Allocation.objects.filter(consultant_id=consultant.id).first()
                        if team_allocation:
                            area = Area.objects.filter(id=team_allocation.area_id).first()
                            if area and area.team_man_email:
                                store.team_mgr = area.team_man_email

                        store.save(update_fields=['sc_name', 'team_mgr'])
                        updated_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Updated Store [{store.store_id}]: sc_email [{consultant.sc_email}], team_mgr [{store.team_mgr}]"
                            )
                        )

        self.stdout.write(self.style.SUCCESS(f" Total Updated: {updated_count}"))
