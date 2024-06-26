from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def _create_user(self,email,password,**extra_fields):
        if not email:
            return ValueError("Please Provide Proper Email Address")
        
        email=self.normalize_email(email)
        user=self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user
    
    def create_user(self,email=None,password=None,**extra_fields):
        extra_fields.setdefault('is_staff',False)
        extra_fields.setdefault('is_superuser',False)
        return self._create_user(email,password,**extra_fields)
    
    def create_superuser(self,email=None,password=None,**extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)
        return self._create_user(email,password,**extra_fields)
    

class UserRegistration(AbstractBaseUser,PermissionsMixin):
    
    email=models.EmailField(unique=True)
    password=models.CharField(max_length=255)
    full_name=models.CharField(max_length=255,null=True,blank=True)
    otp=models.IntegerField(null=True,blank=True)
    otp_created_at=models.DateTimeField(auto_now_add=True,null=True,blank=True)
    user_created_at=models.DateTimeField(auto_now_add=True,null=True,blank=True)
    is_staff=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)
    is_superuser=models.BooleanField(default=False)
    is_valid=models.BooleanField(default=False)
    is_verified=models.BooleanField(default=False)
    is_registered=models.BooleanField(default=False)
    address=models.CharField(max_length=255,null=True,blank=True)
    
    objects=CustomUserManager()
    
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=[]
    
    def __str__(self):
        return f"{self.email}"
    
    
    
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    actual_price = models.DecimalField(max_digits=10, decimal_places=2)
    average_rating = models.FloatField()
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    crawled_at = models.DateTimeField()
    description = models.TextField()
    discount = models.CharField(max_length=255)
    images = models.TextField()  # You might want to use a more appropriate field type for storing multiple image URLs
    out_of_stock = models.BooleanField(default=False)
    pid = models.CharField(max_length=255,null=True,blank=True)
    product_details = models.TextField()
    seller = models.CharField(max_length=255)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)


    def __str__(self):
        return self.title

class PurchaseHistory(models.Model):
    user = models.ForeignKey(UserRegistration, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} purchased {self.product} on {self.purchase_date}"

