from django.contrib import admin

from apps.users.models import User, Address

admin.site.register(User)
admin.site.register(Address)
