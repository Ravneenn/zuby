from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
# Create your models here.


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password = None, **extra_fields):
        if not email:
            raise ValueError('Email is required')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using= self._db)
        return user

    def create_superuser(self, email, password = None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    email = models.CharField(max_length=200, unique=True)
    username = models.CharField(max_length=50, unique=True)
    objects = CustomUserManager()
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    picture = models.ImageField(upload_to='profile_pictures', null=True, blank=True, default='profile_pictures\profile.png')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    slug = models.SlugField(blank=True, unique=True, db_index=True, editable = False, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.first_name + " " + self.last_name  
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.username)
        super().save(args, **kwargs)

class Color(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7)

class Size(models.Model):
    size = models.IntegerField(null=False)
    year = models.CharField(max_length=10, null=False)

class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(blank=True, unique=True, db_index=True, editable = False, null=True)
    

    def __str__(self):
        return self.name 
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(args, **kwargs)

class Product(models.Model):
    class Status(models.TextChoices):
        STOKTA = 'stokta', _('Stokta')
        STOK_YOK = 'stok_yok', _('Stok Yok')
        SATISA_KAPALI = 'satisa_kapali', _('Satışa Kapalı')

    name = models.CharField(max_length=100, verbose_name="Ürün Adı")
    description = models.CharField(max_length=500, verbose_name="Ürün Açıklaması")
    stock = models.IntegerField(verbose_name="Stok Miktarı")
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.STOKTA,
        verbose_name="Durum"
    )
    colors = models.ManyToManyField("core.Color", verbose_name="Renk Seçenekleri")
    sizes = models.ManyToManyField("core.Size", verbose_name="Beden Seçenekleri")
    seo_tags = models.CharField(max_length=250, verbose_name="SEO Etiketleri")
    slug = models.SlugField(blank=True, unique=True, db_index=True, editable=False, null=True, verbose_name="Slug")

    def __str__(self):
        return self.name 
    
    def save(self, *args, **kwargs):
        if self.stock == 0:
            self.status = self.Status.STOK_YOK
        elif not self.status:  # Eğer statü belirtilmemişse
            self.status = self.Status.STOKTA

        self.slug = slugify(self.name)
        super().save(*args, **kwargs)