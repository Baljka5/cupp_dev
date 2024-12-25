from django.core.management.base import BaseCommand
from pymongo import MongoClient
import MySQLdb
from django.conf import settings

class Command(BaseCommand):
    help = 'Sync use_yn from MongoDB to MySQL based on matching store IDs'

    def handle(self, *args, **options):
        client = MongoClient('mongodb://10.10.90.230/')
        db = client.nubia_db
        collection = db.bgf_hq_bizloc_mst

        mysql_conn = MySQLdb.connect(host='10.10.90.34',
                                     user='cumongol_remote',
                                     password='P@$$_cupp123',
                                     db='cupp')
        cursor = mysql_conn.cursor()

        mongo_documents = collection.find({}, {'bizloc_cd': 1, 'use_yn': 1})
        for document in mongo_documents:
            bizloc_cd = document.get('bizloc_cd')
            use_yn = document.get('use_yn')

            if bizloc_cd and use_yn is not None:
                update_query = """
                UPDATE store_consultant
                SET use_yn = %s
                WHERE store_id = %s
                """
                cursor.execute(update_query, (use_yn, bizloc_cd))

        mysql_conn.commit()
        cursor.close()
        mysql_conn.close()
        client.close()
        self.stdout.write(self.style.SUCCESS('Successfully synced use_yn based on store_id and bizloc_cd.'))
