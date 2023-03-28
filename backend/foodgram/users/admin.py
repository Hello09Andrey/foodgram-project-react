from django.contrib import admin
from .models import CustomUser, Follow


class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'email',
        'username',
        'first_name',
        'last_name',
        'password',
    )
    list_filter = ('email', 'username')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Follow)
