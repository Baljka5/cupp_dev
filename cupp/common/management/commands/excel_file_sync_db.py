import pandas as pd
from django.core.management.base import BaseCommand
from cupp.store_consultant.models import StoreConsultant  # ⚠️ өөрийн app path-д тохируулна уу


class Command(BaseCommand):
    help = 'Update StoreConsultant fields from a predefined Excel file using store_id'

    def handle(self, *args, **kwargs):
        excel_file = 'Book1.xlsx'

        try:
            df = pd.read_excel(excel_file, dtype={'store_id': str, 'Store ID': str})  # ✅ store_id-г str болгоно
            df.columns = [col.strip() for col in df.columns]
            print("📄 Excel columns:", df.columns.tolist())

            if 'Store ID' in df.columns and 'store_id' not in df.columns:
                df.rename(columns={'Store ID': 'store_id'}, inplace=True)

            print(f"✅ store_id багана байна уу: {'store_id' in df.columns}")
            print(f"📊 store_id null биш мөрүүд: {df['store_id'].notna().sum()}")
            print(f"📊 store_id жишээ утгууд: {df['store_id'].dropna().astype(str).unique()[:10]}")

        except Exception as e:
            self.stderr.write(f"❌ Excel файл уншиж чадсангүй: {e}")
            return

        updated = 0
        skipped = 0

        for _, row in df.iterrows():
            store_id = str(row.get('store_id')).strip()
            if not store_id or store_id.lower() == 'nan':
                skipped += 1
                continue

            try:
                obj = StoreConsultant.objects.get(store_id=store_id)

                for field in row.index:
                    if field != 'store_id' and hasattr(obj, field) and pd.notna(row[field]):
                        setattr(obj, field, row[field])

                obj.save()
                updated += 1
                self.stdout.write(f"✅ Updated store_id: {store_id}")

            except StoreConsultant.DoesNotExist:
                self.stderr.write(f"⚠ store_id {store_id} олдсонгүй")
                skipped += 1
            except Exception as e:
                self.stderr.write(f"❌ store_id {store_id} update хийхэд алдаа гарлаа: {e}")
                skipped += 1

        self.stdout.write(f"\n✔️ Нийт: {updated} амжилттай, {skipped} алгасагдсан.")

