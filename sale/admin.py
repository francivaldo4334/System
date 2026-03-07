from django.contrib import admin
from sale.models import *

# Register your models here.
admin.site.register(Account)
admin.site.register(Transaction)
admin.site.register(JournalEntry)
# admin.site.register(JournalEntryPositive)
