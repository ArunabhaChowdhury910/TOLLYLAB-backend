from django.contrib.auth.models import User
from django.db import models
from PIL import Image


class GalleryImage(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='gallery/')
    created_at = models.DateTimeField(auto_now_add=True)
    orientation = models.CharField(max_length=10, blank=True)  # Add this field

    def save(self, *args, **kwargs):
        # Auto-detect orientation if not set
        if not self.orientation:
            from PIL import Image
            img = Image.open(self.image)
            if img.width > img.height:
                self.orientation = 'landscape'
            else:
                self.orientation = 'portrait'
        super(GalleryImage, self).save(*args, **kwargs)

    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    category = models.CharField(max_length=100)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image_orientation = models.CharField(max_length=10, blank=True, editable=False)  # New field for image orientation
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Override the save method to determine image orientation
        if self.image:
            with Image.open(self.image) as img:
                width, height = img.size
                if width > height:
                    self.image_orientation = 'landscape'
                else:
                    self.image_orientation = 'portrait'
        super(Product, self).save(*args, **kwargs)


class Testimonial(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    message = models.TextField()
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Testimonial by {self.user.username} on {self.product.name}"


# models.py
from django.db import models
from django.contrib.auth.models import User
from .models import Product

class Order(models.Model):
    customer_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_partner = models.CharField(max_length=255, blank=True, null=True)  # Admin will fill this in later
    tracking_id = models.CharField(max_length=255, blank=True, null=True)  # Admin will fill this in later
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.customer_name}"
