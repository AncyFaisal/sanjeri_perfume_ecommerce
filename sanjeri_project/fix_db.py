import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sanjeri_project.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("ALTER TABLE sanjeri_app_customuser RENAME COLUMN referral_token TO referral_code;")
    print("Renamed column successfully.")
