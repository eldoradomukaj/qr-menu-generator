import os, random, datetime
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.conf import settings
from localflavor.us.models import USStateField, USZipCodeField
from django.utils.translation import gettext as _
from django.db.models.signals import pre_save, post_save
from django.utils.html import mark_safe
from django.dispatch import receiver
from NoMenu.utils import unique_slug_generator

# Create your models here.

def user_directory_path(instance, filename):
    basefilename, file_extension = os.path.splitext(filename)
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
    randomstr = ''.join((random.choice(chars)) for x in range(15))

    return 'uploads/{0}/profile/{1}{2}'.format(instance.cust_pk, randomstr, file_extension)

class Restaurant(models.Model):
    cust_pk = models.CharField(max_length=6, primary_key=True, editable=False, unique=True)
    rest_logo = models.ImageField(null=True, blank=True, upload_to=user_directory_path)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=99, blank=True, null=True)
    address1 = models.CharField(max_length=99, blank=True, null=True)
    address2 = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = USStateField(blank=True, null=True)
    zipcode = USZipCodeField(blank=False, null=True)
    phone = models.CharField(max_length=20, blank=True)
    is_live = models.BooleanField(default=False)
    is_demo = models.BooleanField(default=False)

    def __str__(self):
        return "%s - (%s: %s)" % (self.name, self.cust_pk, self.owner)

    def get_absolute_url(self):
        return reverse('order', kwargs={'pk': self.cust_pk})

    @property
    def google_maps_url(self):
        def process_segment(s):
            return s.replace(" ", "+").replace(",", "%2C")

        out = "https://www.google.com/maps/search/?api=1&query="
        out += process_segment(self.address1) + "%2C+"
        if self.address2:
            out += process_segment(self.address2) + "%2C+"
        out += process_segment(self.city) + "%2C+"
        out += process_segment(self.state) + "+"
        out += process_segment(self.zipcode)

        return out

    def save(self, *args, **kwargs):
        if not self.cust_pk:
            self.cust_pk = get_random_string(length=6, allowed_chars='0123456789')
        return super(Restaurant, self).save(*args, **kwargs)

        
def cat_directory_path(instance, filename):
    basefilename, file_extension = os.path.splitext(filename)
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
    randomstr = ''.join((random.choice(chars)) for x in range(15))

    return 'uploads/{0}/category/{1}{2}'.format(instance.restaurant.cust_pk, randomstr, file_extension)

class Category(models.Model):
    slug = models.SlugField(max_length=100, null=True)
    position = models.DecimalField(max_digits=3, default=0, decimal_places=0)
    is_shown = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True)
    cat_name = models.CharField(max_length=50, blank=True, null=True)
    cat_img = models.ImageField(null=True, blank=True, upload_to=cat_directory_path)
    description = models.CharField(max_length=256, null=True, blank=True)

    class Meta:
        unique_together = ['restaurant', 'cat_name']
    
    def __str__(self):
        return "%s - (%s: %s)" % (self.cat_name.title(), self.restaurant.cust_pk, self.restaurant.owner)
    
    def save(self, *args, **kwargs):
        self.cat_name = self.cat_name and self.cat_name.lower()

        # set our position to the highest existing position + 1
        categories = Category.objects.filter(restaurant=self.restaurant)
        if len(categories) > 0:
            highest_pos = int(max((c.position for c in categories)))
            self.position = highest_pos + 1

        super(Category, self).save(*args, **kwargs)

def pre_save_receiver(sender, instance, *args, **kwargs): 
    if not instance.slug: 
        instance.slug = unique_slug_generator(instance) 

pre_save.connect(pre_save_receiver, sender = Category) 


def menu_directory_path(instance, filename):
    basefilename, file_extension = os.path.splitext(filename)
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
    randomstr = ''.join((random.choice(chars)) for x in range(15))
    
    return 'uploads/{0}/menu/{1}{2}'.format(instance.owner.pk, randomstr, file_extension)

class Menu(models.Model):
    # default options for "units" field
    # database item : human readable
    UNIT_CHOICES = {
        "EA": "each",
        "OZ": "per ounce",
        "LB": "per pound",
        "OT": "other",
    }

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    owner = models.ForeignKey(Restaurant, to_field='cust_pk', null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=100)
    price = models.DecimalField(decimal_places=2, max_digits=1000, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(blank=True, upload_to=menu_directory_path)
    image_url = models.CharField(max_length=400, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    is_shown = models.BooleanField(default=True)
    units = models.CharField(
        max_length=2,
        choices=UNIT_CHOICES.items(),
        default="EA"
    )
    custom_unit = models.CharField(max_length=64, blank=True)
    allergens = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return "%s - (%s : %s)" % (self.title.title(), self.owner.cust_pk, self.owner.owner)

    def get_absolute_url(self):
        return reverse('item', kwargs={'pk': self.owner.cust_pk, 'cat_id': self.category.slug, 'item_id': self.pk})

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

    @property
    def priceString(self):
        base = "$" + str(self.price)
        if self.units == "EA":
            return base
        base += " "
        if self.units == "OT":
            return base + self.custom_unit
        return base + self.UNIT_CHOICES[self.units]



HOUR_OF_DAY_24 = [(i,i) for i in range(1,25)]
WEEKDAYS = (
    (0, _("Monday")),
    (1, _("Tuesday")),
    (2, _("Wednesday")),
    (3, _("Thursday")),
    (4, _("Friday")),
    (5, _("Saturday")),
    (6, _("Sunday"))
)


class RestaurantHours(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    monday = models.BooleanField(default=True)
    monday_hours = models.CharField(max_length=256)
    tuesday = models.BooleanField(default=True)
    tuesday_hours = models.CharField(max_length=256)
    wednesday = models.BooleanField(default=True)
    wednesday_hours = models.CharField(max_length=256)
    thursday = models.BooleanField(default=True)
    thursday_hours = models.CharField(max_length=256)
    friday = models.BooleanField(default=True)
    friday_hours = models.CharField(max_length=256)
    saturday = models.BooleanField(default=True)
    saturday_hours = models.CharField(max_length=256)
    sunday = models.BooleanField(default=True)
    sunday_hours = models.CharField(max_length=256)

    def __str__(self):
        return "%s" % (self.restaurant)

class SpecialDays(models.Model):
    holiday_date = models.DateField()
    closed = models.BooleanField(default=True)
    from_hour = models.PositiveSmallIntegerField(choices=HOUR_OF_DAY_24, null=True, blank=True)
    to_hour = models.PositiveSmallIntegerField(choices=HOUR_OF_DAY_24, null=True, blank=True)


class TableNumber(models.Model):
    table = models.CharField(max_length=10, null=True, blank=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

class Order(models.Model):
    ORDER_STATUS = (
        ('ORDERED', 'ORDERED'),
        ('CONFIRMED', 'CONFIRMED'),
        ('IN PROGRESS', 'IN PROGRESS'),
        ('READY', 'READY'),
        ('COMPLETE', 'COMPLETE'),
        ('CANCELLED', 'CANCELLED'),
    )

    device = models.CharField(max_length=300, null=True, blank=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT)
    table_number = models.CharField(max_length=100, null=True, blank=True)
    order_number = models.CharField(max_length=7, editable=False, unique=True)
    quantity = models.PositiveIntegerField(null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=99, blank=True, null=True)
    address1 = models.CharField(max_length=99, blank=True, null=True)
    address2 = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = USStateField(blank=True, null=True)
    zipcode = USZipCodeField(blank=False, null=True)
    phone = models.CharField(max_length=20, blank=True)
    order_status = models.CharField(choices=ORDER_STATUS, max_length=200, null=True, blank=True, default="")
    order_type = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return "%s" % (self.order_number)

    @property
    def get_date(self):
        return self.date_ordered.strftime("%m/%d/%Y %H:%M")

    @property
    def order_total(self):
        return sum(
            ((i.item.price * i.quantity) for i in OrderItem.objects.filter(order=self))
        )
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = get_random_string(length=7, allowed_chars='0123456789')
        #if not self.date_ordered:
        #    self.date_ordered = datetime.datetime.now()
        return super(Order, self).save(*args, **kwargs)
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    item = models.ForeignKey(Menu, on_delete=models.PROTECT)
    # price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    quantity = models.DecimalField(max_digits=6, decimal_places=2, default=1.0)
    special_instructions = models.TextField(max_length=400, null=True, blank=True)

    # def get_item_price(self):
    #     self.price = self.item.price

    def __str__(self):
        return "%s" % (self.item.title)

    @property
    def total_price(self) -> str:
        return str(self.quantity * self.item.price)


class Favorite(models.Model):
    device = models.CharField(max_length=300, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    item = models.ForeignKey(Menu, on_delete=models.CASCADE)

    def __str__(self):
        return self.item.title
