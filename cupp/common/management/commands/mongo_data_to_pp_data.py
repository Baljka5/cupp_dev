from django.core.management.base import BaseCommand
from pymongo import MongoClient
import MySQLdb


class Command(BaseCommand):
    help = 'Sync use_yn, sal_prc_grd_tp, and bizloc_tp from MongoDB to MySQL based on matching store IDs'

    def handle(self, *args, **options):
        # Connect to MongoDB
        client = MongoClient('mongodb://admin:CE2dmin22@10.10.90.230/')
        db = client.nubia_db
        collection = db.bgf_hq_bizloc_mst

        # Connect to MySQL
        mysql_conn = MySQLdb.connect(host='10.10.90.34',
                                     user='cumongol_remote',
                                     password='P@$$_cupp123',
                                     db='cupp',
                                     charset='utf8mb4')
        cursor = mysql_conn.cursor()

        # Fetch necessary fields from MongoDB
        mongo_documents = collection.find({}, {'bizloc_cd': 1, 'use_yn': 1, 'sal_prc_grd_tp': 1, 'bizloc_tp': 1,
                                               'ost_dt': 1, 'cls_dt': 1, 'bizloc_nm': 1})

        # Prepare batch update data
        update_data = []
        for document in mongo_documents:
            bizloc_cd = document.get('bizloc_cd')
            use_yn = document.get('use_yn')
            sal_prc_grd_tp = document.get('sal_prc_grd_tp')
            bizloc_tp = document.get('bizloc_tp')
            ost_dt = document.get('ost_dt')
            cls_dt = document.get('cls_dt')
            bizloc_nm = document.get('bizloc_nm')

            if bizloc_cd is not None:
                update_data.append((use_yn, sal_prc_grd_tp, bizloc_tp, ost_dt, cls_dt, bizloc_nm, bizloc_cd))

        # Execute batch update using executemany for better performance
        if update_data:
            update_query = """
            UPDATE store_consultant
            SET use_yn = %s, prc_grade = %s, store_type = %s, ost_dt = %s, cls_dt = %s, store_name = %s
            WHERE store_id = %s
            """
            cursor.executemany(update_query, update_data)

        # Commit changes and close connections
        mysql_conn.commit()
        cursor.close()
        mysql_conn.close()
        client.close()

        self.stdout.write(self.style.SUCCESS(
            'Successfully synced use_yn, prc_grade, and store_type based on store_id and bizloc_cd.'))
