# admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Subject, Tag, Document

class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    # Add your custom forms here if needed

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    list_display = ('email', 'is_admin', 'is_moderator', 'is_verified')
    list_filter = ('is_admin', 'is_moderator', 'is_verified')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_admin', 'is_moderator', 'is_verified')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_admin', 'is_moderator', 'is_verified'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)
admin.site.register(Subject)
admin.site.register(Tag)
admin.site.register(Document)