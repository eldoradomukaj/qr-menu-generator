from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _

# Create your models here.

class SignUpCode(models.Model):
    signup_code = models.CharField(max_length=10, unique=True, null=True, blank=True)

    def __str__(self):
        return self.signup_code or ''

def user_profile_img_path(instance, filename):
    basefilename, file_extension = os.path.splitext(filename)
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
    randomstr = ''.join((random.choice(chars)) for x in range(15))

    return 'uploads/profile_{0}/{1}{2}'.format(instance.user, randomstr, file_extension)

class User(AbstractUser):
    username = models.CharField(blank=True, null=True, max_length=100)
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=50, blank=True)
    phone_number = models.CharField(max_length=12)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    is_active = models.BooleanField(_('active'), default=True)
    setup_complete = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']

    def get_username(self):
        return self.email

    def __str__(self):
        return "%s %s (%s)" % (self.first_name.title(), self.last_name.title(), self.email)