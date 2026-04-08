import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sanjeri_project.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='sanjeri_app_coupon'")
    columns = cursor.fetchall()
    print("sanjeri_app_coupon columns:")
    for col in columns:
        print(col)
        
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_name='sanjeri_app_referraloffer'")
    tables = cursor.fetchall()
    print("sanjeri_app_referraloffer table exists:", len(tables) > 0)
