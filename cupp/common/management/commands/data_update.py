import pandas as pd
from django.core.management.base import BaseCommand
from django.db import connection, transaction


class Command(BaseCommand):
    help = "Update store_planning and store_consultant tables using Excel file"

    def handle(self, *args, **kwargs):
        excel_path = "Result_1_Solongo.xlsx"
        df = pd.read_excel(excel_path)

        # 🔍 store_id-г зөв хэлбэрт оруулна
        df = df.dropna(subset=["store_id"])
        df["store_id"] = df["store_id"].astype(str).str.zfill(5)

        updated_count = 0

        with transaction.atomic():
            with connection.cursor() as cursor:
                for idx, row in df.iterrows():
                    store_id = row["store_id"]

                    address_det = str(row.get("address_det", "")).strip()
                    tt_type = str(row.get("tt_type", "")).strip()
                    wday_hours = str(row.get("wday_hours", "")).strip()
                    wend_hours = str(row.get("wend_hours", "")).strip()
                    store_email = str(row.get("store_email", "")).strip()

                    # Update store_planning
                    cursor.execute("""
                        UPDATE store_planning
                        SET address_det = %s
                        WHERE store_id = %s
                    """, [address_det, store_id])

                    # Update store_consultant
                    cursor.execute("""
                        UPDATE store_consultant
                        SET tt_type = %s,
                            wday_hours = %s,
                            wend_hours = %s,
                            store_email = %s
                        WHERE store_id = %s
                    """, [tt_type, wday_hours, wend_hours, store_email, store_id])

                    updated_count += 1

        self.stdout.write(self.style.SUCCESS(f"✅ {updated_count} мөрийг амжилттай шинэчиллээ."))
