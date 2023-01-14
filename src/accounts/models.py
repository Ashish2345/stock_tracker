from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from django.conf import settings
from django.contrib.auth.models import Group

from datetime import datetime

from PIL import Image 
from io import BytesIO
from django.core.files import File


def profile_pic_path(self, filename):
    time_stamp = datetime.now().strftime("%Y%M%d%H%M")
    return f'accounts/{self.pk}/{time_stamp}/{"profile_image.jpeg"}'


def reduce_image_size(image):
    # Open the image
    im = Image.open(image).convert("RGB")
    # Set the desired size
    size = (170, 170)
    # Resize the image
    im = im.resize(size, Image.ANTIALIAS)
    # Save the image to a BytesIO object
    buffer = BytesIO()
    im.save(buffer, 'jpeg', quality=30)

    # Save the BytesIO object to the image field
    new_image = File(buffer, name=image.name)
    return new_image


class UserManager(BaseUserManager):

    def create_user(self, email, first_name, last_name ,is_active, password=None):
        if not email:
            raise ValueError("User must have an email")
        if not is_active:
            raise ValueError("User must have an active status")
        if not first_name:
            raise ValueError("User must have an first name")
        if not last_name:
            raise ValueError("User must have an last name")

        user_obj = self.model(
            email=self.normalize_email(email),
            is_active=is_active,
            first_name=first_name,
            last_name=last_name)

        user_obj.set_password(password)
        user_obj.save(using=self._db)
        return user_obj

    def create_superuser(self, email, first_name, last_name, password):
        user = self.create_user(
            email=self.normalize_email(email),
            is_active=True,
            first_name=first_name,
            last_name=last_name,
            password=password)
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    first_name = models.CharField(max_length=50, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=50, verbose_name=_("Last Name"))
    email = models.EmailField(max_length=100, verbose_name=_("Email"), unique=True)
    username = models.CharField(max_length=150, null=True)
    is_admin = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(verbose_name='Last login',auto_now=True)
    is_verified_email = models.BooleanField(default=False)
    profile_pic = models.FileField(_("Profile Picture"), 
                    upload_to=profile_pic_path, validators=[FileExtensionValidator(allowed_extensions=settings.VALID_FILE_EXTENSIONS)], null=True)
    role = models.ForeignKey(Group, verbose_name=_("User Role"), on_delete=models.SET_NULL, null=True)

    objects = UserManager()
    REQUIRED_FIELDS = ['first_name', 'last_name']
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name_plural = "Users"

    def save(self, *args, **kwargs):
        if self.id and self.profile_pic and self.profile_pic != self.__class__.objects.get(id=self.id).profile_pic:
            self.profile_pic = reduce_image_size(self.profile_pic)
        super(self.__class__,self).save(*args, **kwargs)

    

    def has_perm(self,perm , obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


class UserActivityLog(models.Model):
    action=models.CharField(max_length=100)
    description=models.CharField(max_length=100)
    action_date=models.DateTimeField(max_length=100)
    action_by=models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='action_user')


