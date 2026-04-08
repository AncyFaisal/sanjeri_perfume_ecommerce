import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sanjeri_project.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='sanjeri_app_customuser'")
    columns = cursor.fetchall()
    for col in columns:
        print(col)
