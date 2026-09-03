"""End-to-end test for the website admin panel + CSV bulk import."""
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realestate.settings')
django.setup()

from django.contrib.auth.models import User  # noqa: E402
from django.core.files import File  # noqa: E402
from django.core.files.uploadedfile import SimpleUploadedFile  # noqa: E402
from django.test import Client  # noqa: E402

from listings.models import Listing, CsvImport  # noqa: E402
from realtors.models import Realtor  # noqa: E402

BASE = os.path.dirname(os.path.abspath(__file__))

# --- Setup: make sure a realtor exists (needed as FK for listings) ---
realtor = Realtor.objects.first()
created_realtor = False
if realtor is None:
    with open(os.path.join(BASE, 'static', 'img', 'homes', 'home-1.jpg'), 'rb') as fh:
        realtor = Realtor.objects.create(
            name='CSV Test Realtor',
            photo=File(fh, name='realtor.jpg'),
            phone='1234567890',
            email='csvtest@example.com',
        )
    created_realtor = True
print('realtor:', realtor)

# Idempotent test users
User.objects.filter(username__in=['csvadmin', 'csvplain']).delete()
staff = User.objects.create_user(
    username='csvadmin', password='CsvAdmin!234', is_staff=True, is_superuser=True)
regular = User.objects.create_user(username='csvplain', password='CsvPlain!234')

csv_header = 'title,address,city,state,zipcode,price,bedrooms,bathrooms,garage,sqft,lot_size,description,realtor,is_published'
file_a = SimpleUploadedFile(
    'batch_a.csv',
    (
        f'{csv_header}\n'
        f'CSV Bulk Test House,1 Test St,Testville,TS,99999,450000,3,2,1,1800,5000,Nice house,CSV Test Realtor,true\n'
        f'CSV Bulk Test Villa,2 Test Ave,Testville,TS,99998,600000,4,3,2,2600,7000,Big villa,,1\n'
    ).encode('utf-8'),
    content_type='text/csv',
)
file_b = SimpleUploadedFile(
    'batch_b.csv',
    (
        f'{csv_header}\n'
        f'CSV Bulk Test House,1 Test St,Testville,TS,99999,499000,3,2,1,1800,5000,Updated description,,true\n'
        f'CSV Bulk Test Broken,3 Test Rd,Testville,TS,99997,,2,1,0,900,2000,Missing price,,1\n'
    ).encode('utf-8'),
    content_type='text/csv',
)
file_not_csv = SimpleUploadedFile('notes.txt', b'not a csv', content_type='text/plain')

client = Client()

print('--- Access control ---')
r = client.get('/accounts/admin-panel/', follow=True)
print('anonymous GET ->', r.status_code, '(expect 200 after redirect to home)')
r = client.post('/accounts/login/', {'username': 'csvplain', 'password': 'CsvPlain!234'})
r = client.get('/accounts/admin-panel/', follow=True)
print('non-staff GET ->', r.status_code, '(expect 200 after redirect to home with error msg)')
client.logout()

r = client.post('/accounts/login/', {'username': 'csvadmin', 'password': 'CsvAdmin!234'})
r = client.get('/accounts/admin-panel/')
print('staff GET panel ->', r.status_code, '(expect 200)',
      '| upload form present:', b'Import Listings from CSV' in r.content)

r = client.get('/accounts/admin-panel/sample-csv/')
print('sample csv ->', r.status_code, r.get('Content-Type', ''), '(expect 200 text/csv)')

print('--- Multi-file CSV upload ---')
listing_count_before = Listing.objects.count()
r = client.post('/accounts/admin-panel/', {
    'csv_files': [file_a, file_b],
    'default_realtor': str(realtor.id),
}, follow=True)
print('upload POST ->', r.status_code, '(expect 200 after redirect back to panel)')
print('upload form still present:', b'Import Listings from CSV' in r.content)

created_listings = Listing.objects.filter(title__startswith='CSV Bulk Test')
print('listings created:', created_listings.count(), '(expect 2)')
imports = list(CsvImport.objects.order_by('created_at'))
print('import records:', len(imports), '(expect 2)')
for imp in imports:
    print('  ->', imp.original_filename,
          '| created:', imp.rows_created, '| updated:', imp.rows_updated,
          '| failed:', imp.rows_failed, '| errors:', repr(imp.errors[:80]))

house = Listing.objects.filter(title__iexact='CSV Bulk Test House').first()
villa = Listing.objects.filter(title__iexact='CSV Bulk Test Villa').first()
print('house price updated to 499000:', house.price == 499000 if house else False)
# 'CSV Test Realtor' does not exist in this DB (first realtor is named 'jim'),
# so BOTH rows must fall back to the chosen default realtor:
print('house realtor fell back to default:', house.realtor.name == 'jim' if house else False)
print('villa realtor fell back to default:', villa.realtor.name == 'jim' if villa else False)
print('villa has placeholder photo:', bool(villa.photo_main) if villa else False)
print('villa published:', villa.is_published if villa else False)
print('listings before/after total:', listing_count_before, '->', Listing.objects.count())

# Non-csv rejection
r = client.post('/accounts/admin-panel/', {
    'csv_files': [file_not_csv],
    'default_realtor': '',
}, follow=True)
print('non-csv upload skipped:', b'only .csv files are supported' in r.content)

# Empty submission
r = client.post('/accounts/admin-panel/', {}, follow=True)
print('empty upload ->', r.status_code, '| warning shown:', b'choose at least one CSV file' in r.content)

print('--- Cleanup ---')
for imp in CsvImport.objects.all():
    imp.file.delete(save=False)
    imp.delete()
created_listings.delete()
staff.delete()
regular.delete()
if created_realtor:
    realtor.delete()
print('cleanup done. listings total now:', Listing.objects.count())
