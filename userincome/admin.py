from django.contrib import admin
from .models import UserIncome, Source
# Register your models here.


class IncomeeAdmin(admin.ModelAdmin):
    list_display = ('amount', 'description', 'owner', 'source', 'date')
    search_fields = ('description', 'source', 'date')
    list_filter = ('source', 'date', 'description')
    ordering = ('-date',)
    list_per_page = 5


admin.site.register(UserIncome, IncomeeAdmin)
admin.site.register(Source)
