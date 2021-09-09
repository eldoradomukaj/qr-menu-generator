from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .forms import UserCreateForm
# Register your models here.

class UserModelAdmin(UserAdmin):
    form = UserCreateForm
    model = User
    readonly_fields = ('date_joined',)

admin.site.register(User)
admin.site.register(SignUpCode)