
import pdb

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

# Create your models here.

def user_directory_path(instance, filename):
    #pdb.set_trace()
    return 'profile/{0}/{1}'.format(instance.user.username, filename)

class UserPhoto(models.Model):
    user = models.OneToOneField(User, related_name='photo')
    photo = models.ImageField(upload_to=user_directory_path, null=True, max_length=255)
    photo_350 = models.ImageField(upload_to=user_directory_path, null=True, max_length=255)
    photo_40 = models.ImageField(upload_to=user_directory_path, null=True, max_length=255)
