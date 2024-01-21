from django.contrib import admin
from .models import User, Food, Order
from django.utils.html import format_html

class UserAdmin(admin.ModelAdmin):
    list_display = ('first_name','last_name')

class FoodAdmin(admin.ModelAdmin):
    list_display = ('name',)
    readonly_fields = ('display_image',)

    def display_image(self, obj):
        return format_html('<img src="{}" width="300" height="300" />'.format(obj.image.url))


admin.site.register(User, UserAdmin)
admin.site.register(Food, FoodAdmin)
admin.site.register(Order)

