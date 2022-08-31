from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
import uuid, os
from django.contrib.auth import get_user_model
User = get_user_model()

def random_file_name(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('uploads', filename)


# Create your models here.
class Search(models.Model):
    address = models.CharField(max_length=200, null=True)
    date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.address
  
    
class Add(models.Model):
    title = models.CharField(max_length=200)
    lat = models.DecimalField(max_digits=9, decimal_places=6, default=0.00)
    lon = models.DecimalField(max_digits=9, decimal_places=6, default=0.00)
    description = models.TextField(default='SOME STRING')
    image = models.ImageField(upload_to=random_file_name, blank=True, null=True)
    
    
    
    date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.title



class Icon(models.Model):
    title = models.CharField(max_length=100)
    icon = models.ImageField(upload_to='icons/', blank=False, null=False)
    size = models.CharField(max_length=20, default="20, 20")
    anchor = models.CharField(max_length=10, default="0, 0")
    
    def __str__(self):
        return self.title
 
    
    
class Toilet(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    lat = models.DecimalField(max_digits=9, decimal_places=6, default=0.00)
    lon = models.DecimalField(max_digits=9, decimal_places=6, default=0.00)
    description = models.TextField(default='SOME STRING')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    icon = models.ForeignKey(Icon, on_delete=models.PROTECT, null = True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    submited = models.BooleanField(default=False)
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title}'
    
       
class ToiletImage(models.Model):
    toilet = models.ForeignKey(Toilet, default=None, on_delete=models.CASCADE)
    images = models.FileField(upload_to=random_file_name, blank=True, null=True)

    def __str__(self):
        return self.toilet.title   


class Rating(models.Model):
    toilet = models.ForeignKey(Toilet, default=None, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0,
                                 validators=[
                                     MaxValueValidator(5),
                                     MinValueValidator(0),
                                 ])


    def __str__(self):
        return f'{self.toilet.title}: {str(self.rating)}'
    
    
class UserSetting(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    bio = models.TextField(default='')

    
    def __str__(self):
        return str(self.user)
    
    
    
class UpdateToilet(models.Model):
    id = models.AutoField(primary_key=True)
    toilet_id = models.ForeignKey(Toilet, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, null=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    lon = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    description = models.TextField(null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    clear = models.BooleanField(default=False)
    #author = models.ForeignKey(User, on_delete=models.CASCADE)
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id}'
    
class UpdateToiletImage(models.Model):
    toilet = models.ForeignKey(UpdateToilet, default=None, on_delete=models.CASCADE)
    images = models.FileField(upload_to=random_file_name, blank=True, null=True)

    def __str__(self):
        return f"{self.toilet.id}"
