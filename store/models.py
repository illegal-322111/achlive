from django.db import models
from django.urls import reverse
from django.utils.text import slugify
# Category Model
class Category(models.Model):
    STATUS_CHOICES = ((-1,'Side Menu'),(0,'USA Banks'), (1,"Canada Banks"), (2,"European Banks"),(3,"Pua and Fullz"))
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    location = models.IntegerField(choices=STATUS_CHOICES, default=-1)
    class Meta:
        verbose_name_plural = 'categories'
        
    def get_absolute_url(self):
        return reverse('category_list',args=[self.slug])
    def number(self):
        if self.id <= 5:
            return self.id * 5 + 3 
        else:
            return self.id * 2 + 4
    def __str__(self):
           return self.name
#PRODUCT MODEL      
class Product(models.Model):
    category = models.ForeignKey(Category, related_name='product', on_delete=models.CASCADE)
    name = models.CharField(max_length=255,help_text="Not shown but required")
    Balance = models.CharField(max_length=255,blank=True)
    Title = models.CharField(max_length=255,blank=True)
    Info = models.TextField(blank=True)
    slug = models.SlugField(max_length=255)
    price = models.FloatField( blank=True,null=True)
    Status = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(null=True, blank=True, upload_to='images/')
    pdf = models.FileField(null=True, blank=True, upload_to='pdfs/')
    
    
    class Meta:
        verbose_name_plural = 'Products'
        ordering = ('created',)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

        # Check if the slug already exists
        if Product.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            # Add a unique suffix to the slug
            self.slug = f"{self.slug}-{self.pk}"
            self.save()
    
    def get_absolute_url(self):
        return reverse('front:product_detail',args=[self.slug])

    def __str__(self):
        return self.name
        