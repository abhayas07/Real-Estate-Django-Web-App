from django import forms
from django.contrib import admin

from .models import Listing, CsvImport
from .services import parse_listing_csv


class ListingAdmin(admin.ModelAdmin):
  list_display = ('id', 'title', 'is_published', 'price', 'list_date', 'realtor')
  list_display_links = ('id', 'title')
  list_filter = ('realtor',)
  list_editable = ('is_published',)
  search_fields = ('title', 'description', 'address', 'city', 'state', 'zipcode', 'price')
  list_per_page = 25


class CsvImportForm(forms.ModelForm):
  """Upload form that accepts one CSV file and imports it immediately."""

  class Meta:
    model = CsvImport
    fields = ['file']
    widgets = {
      'file': forms.FileInput(attrs={'accept': '.csv,text/csv'}),
    }
    labels = {
      'file': 'CSV file with listing data',
    }


@admin.register(CsvImport)
class CsvImportAdmin(admin.ModelAdmin):
  form = CsvImportForm
  list_display = ('original_filename', 'rows_created', 'rows_updated',
                  'rows_failed', 'uploaded_by', 'created_at')
  list_display_links = ('original_filename',)
  readonly_fields = ('original_filename', 'rows_created', 'rows_updated',
                     'rows_failed', 'errors', 'uploaded_by', 'created_at')
  list_per_page = 25

  def save_model(self, request, obj, form, change):
    if not change and form.cleaned_data.get('file'):
      stats = parse_listing_csv(form.cleaned_data['file'])
      obj.original_filename = stats['filename']
      obj.rows_created = stats['created']
      obj.rows_updated = stats['updated']
      obj.rows_failed = stats['failed']
      obj.errors = '\n'.join(stats['errors'])
      obj.uploaded_by = request.user
    super().save_model(request, obj, form, change)


admin.site.register(Listing, ListingAdmin)