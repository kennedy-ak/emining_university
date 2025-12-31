"""
Custom data dump script with UTF-8 encoding support
"""
import os
import sys
import django
import json
from io import StringIO

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emining_university.settings')
django.setup()

from django.core.management import call_command
from django.core.management.commands.dumpdata import Command

# Create a StringIO object to capture output
output = StringIO()

# Run dumpdata command and capture output
call_command(
    'dumpdata',
    natural_foreign=True,
    natural_primary=True,
    exclude=['contenttypes', 'auth.Permission', 'sessions', 'admin.logentry'],
    indent=2,
    stdout=output
)

# Get the JSON string
json_data = output.getvalue()

# Write to file with UTF-8 encoding
with open('backup_data.json', 'w', encoding='utf-8') as f:
    f.write(json_data)

print("Data backup completed successfully!")
print(f"Backup file size: {len(json_data)} bytes")
