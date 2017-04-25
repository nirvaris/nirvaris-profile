from django.contrib import admin

# Register your models here.

from .models import UserPhoto



class UserPhotoAdmin(admin.ModelAdmin):
    list_display = ('user','photo_url',)

admin.site.register(UserPhoto, UserPhotoAdmin)
