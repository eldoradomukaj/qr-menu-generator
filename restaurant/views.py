from typing import List
from urllib.parse import unquote
import json, os, random

from django.contrib import messages
from django.core.mail import BadHeaderError, EmailMessage
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Restaurant, Category, RestaurantHours, Order, OrderItem, Menu, Favorite
from .forms import BugReportForm, RestaurantOrderForm
from django.utils.crypto import get_random_string

from django.conf import settings

import boto3

# Create your views here.

# def random_category():
#     session = boto3.session.Session(
#         aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#         aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
#     )
    
#     s3 = session.resource('s3')
#     my_bucket = s3.Bucket('nomenu-prod')

#     arr = []

#     for i in my_bucket.objects.filter(Delimiter='/', Prefix='static/images/'):
#         arr.append(i.key)
        
    
#     random_img = random.choice(arr)
#     a, b, c = random_img.split('/')
#     new_img = "{}/{}".format(b, c)

#     return new_img
    
    

def restaurant_view(request, pk):
    obj: Restaurant = get_object_or_404(Restaurant, cust_pk=pk)

    device_id: str = request.COOKIES.get('device')
    try:
        order_obj: Order = Order.objects.get(
            device=device_id,
            restaurant=obj,
        )
    except Order.DoesNotExist:
        order_obj: Order = Order.objects.create(
            device=device_id,
            restaurant=obj,
        )
    order_has_items: bool = len(OrderItem.objects.filter(order=order_obj)) > 0

    hours = RestaurantHours.objects.get(restaurant=obj)

    menu = Menu.objects.filter(owner=pk)
    category = Category.objects.filter(restaurant=pk).order_by('position')

    fav_items: Favorite = Favorite.objects.filter(restaurant=pk, device=device_id)
    fav: Favorite = [i.item.id for i in fav_items]

    bug_report_form: BugReportForm
    if request.method == 'GET':
        bug_report_form = BugReportForm()
    else:
        bug_report_form = BugReportForm(request.POST)
        if bug_report_form.is_valid():
            # message = "Name: " + name + "\nemail: " + from_email + " \n \n" + form.cleaned_data['message']
            message: str = "Restaurant: {} (ID {})\n \n".format(obj.name, str(obj.cust_pk))
            message += bug_report_form.cleaned_data['message']
            message += "\n\nAttached is a copy of the user's browser data."
            subject: str = "Bug report for restaurant " + obj.name
            try:
                mail: EmailMessage = EmailMessage(subject, message, 'contact@nomenu.io', ['contact@nomenu.io'])
                mail.attach('browser_data.txt', bug_report_form.cleaned_data['browser_data'], 'text/plain')
                mail.send()

                bug_report_form = BugReportForm()
                messages.success(request, "Bug report sent successfully.")
            except BadHeaderError:
                messages.error(request, "Could not send bug report.")

    context = {
        'bug_report_form': bug_report_form,
        'obj': obj,
        'menu': menu,
        'hours': hours,
        'categories': category,
        'order_has_items': order_has_items,
        'fav_items': fav
    }
    return render(request, 'restaurant/menu.html', context)


def category_view(request, pk, id):
    device: str = request.COOKIES.get('device')
    obj = get_object_or_404(Restaurant, cust_pk=pk)

    hours = RestaurantHours.objects.get(restaurant=obj)
    

    category = get_object_or_404(Category, restaurant=pk, slug=id)

    menu_items: Menu = Menu.objects.filter(owner=pk, category__slug=id).order_by('-image', '-image_url', 'title' )
    fav_items: Favorite = Favorite.objects.filter(restaurant=pk, device=device)

    fav: Favorite = [i.item.id for i in fav_items]

    context = {
        'obj': obj,
        'category_page': 'active',
        'category': category,
        'menu_items': menu_items,
        'fav_items': fav,
        'hours': hours
    }
    return render(request, 'restaurant/category.html', context)


def item_view(request, pk, cat_id, item_id):
    restaurant = get_object_or_404(Restaurant, cust_pk=pk)
    category = Category.objects.filter(restaurant=pk, cat_name=cat_id)
    obj = get_object_or_404(Menu, owner=restaurant, id=item_id)

    hours = RestaurantHours.objects.get(restaurant=restaurant)

    device_id: str = request.COOKIES.get('device')

    if request.method == "POST":
        
        try:
            order_obj: Order = Order.objects.get(
                device=device_id,
                restaurant=restaurant,
            )
        except Order.DoesNotExist:
            order_obj: Order = Order.objects.create(
                device=device_id,
                restaurant=restaurant,
            )

        order_item: OrderItem = OrderItem.objects.create(
            order=order_obj,
            item=obj,
            quantity=float(request.POST['quantity']),
            special_instructions=str(request.POST.get('special-instructions'))
        )

        #return redirect('order', pk=restaurant.cust_pk)
    
    fav_items: Favorite = Favorite.objects.filter(restaurant=pk, device=device_id)
    fav: Favorite = [i.item.id for i in fav_items]

    context = {
        'obj': obj,
        'category': category,
        'restaurant': restaurant,
        'fav_items': fav,
        'hours': hours
    }
    return render(request, 'restaurant/item.html', context)


def order_view(request, pk):
    restaurant = get_object_or_404(Restaurant, cust_pk=pk)
    device_id: str = request.COOKIES.get('device')
    try:
        order_obj: Order = Order.objects.get(
            device=device_id,
            restaurant=restaurant,
        )
    except Order.DoesNotExist:
        order_obj: Order = Order.objects.create(
            device=device_id,
            restaurant=restaurant,
        )

    context = {
        'restaurant': restaurant,
        'order_total': order_obj.order_total,
        'order_items': OrderItem.objects.filter(
            order=order_obj,
        ),
    }
    return render(request, 'restaurant/order.html', context)

def remove_order_item(request, pk):
    restaurant = get_object_or_404(Restaurant, cust_pk=pk)
    device_id: str = request.COOKIES.get('device')
    try:
        order_obj: Order = Order.objects.get(
            device=device_id,
            restaurant=restaurant,
        )
        
    except Order.DoesNotExist:
        order_obj: Order = Order.objects.create(
            device=device_id,
            restaurant=restaurant,
        )

    if request.is_ajax():
        item_name: str = request.GET.get('item_name', '')
        
        order_items: OrderItem = OrderItem.objects.filter(id=item_name)

        try:
            item: Menu = [i.id for i in order_items]
            
        except IndexError:
            raise Http404("Item {} not found".format(item_name))
        
        order_items \
            .filter(id=item[0]) \
            .delete()
        return HttpResponse("")
    else:
        return HttpResponse("Nothing to see here.")

def modify_item_quantity(request, pk):
    restaurant = get_object_or_404(Restaurant, cust_pk=pk)
    device_id: str = request.COOKIES.get('device')
    try:
        order_obj: Order = Order.objects.get(
            device=device_id,
            restaurant=restaurant,
        )
    except Order.DoesNotExist:
        order_obj: Order = Order.objects.create(
            device=device_id,
            restaurant=restaurant,
        )

    if request.is_ajax():
        item_name: str = request.GET.get('item_name', '')
        
        new_quantity: int = int(request.GET.get('new_quantity', ''))
        order_items: List[OrderItem] = OrderItem.objects.filter(order=order_obj)

        try:
            item: Menu = [i.item for i in order_items if i.item.title == item_name][0]
        except IndexError:
            raise Http404("Item {} not found".format(item_name))

        order_item: OrderItem = order_items.get(item=item)
        order_item.quantity = new_quantity
        order_item.save()

        return JsonResponse({"newPrice": order_item.total_price})
    else:
        return HttpResponse("Nothing to see here.")

def get_order_items(request):
    response_data = {}

    device = request.COOKIES.get('device')
    cookies = request.COOKIES['nomenu-order']
    order = json.loads(unquote(cookies)) if cookies else []

    for i in order:
        print("item id: ", i['id'])
        print("quantity: ", i['quantity'])


    return JsonResponse(response_data)

def inrestaurant_checkout_view(request, pk):
    restaurant = get_object_or_404(Restaurant, cust_pk=pk)

    device_id = request.COOKIES.get('device')
    name = request.POST.get('name')
    table_number = request.POST.get('table_number')

    try:
        order_obj: Order = Order.objects.filter(
            device=device_id,
            restaurant=restaurant,
        )
    except Order.DoesNotExist:
        order_obj: Order = Order.objects.create(
            device=device_id,
            restaurant=restaurant,
        )
    
    order_form = RestaurantOrderForm()

    if request.method == 'POST':
        order_form = RestaurantOrderForm(request.POST)
        if order_form.is_valid():
            order_obj.update(name=name, table_number=table_number, order_status="ORDERED")
            response = HttpResponseRedirect(reverse('menu', args=(pk,)))
            response.delete_cookie('device')

            return response

    context = {
        'order_form': order_form,
        'restaurant': restaurant
    }

    return render(request, 'restaurant/in_restaurant_checkout.html', context)

def carryout_checkout_view(request, pk):
    context = {}

    return render(request, 'restaurant/carryout_checkout.html', context)


def get_favorites_view(request, pk):
    obj = get_object_or_404(Restaurant, cust_pk=pk)
    hours = RestaurantHours.objects.get(restaurant=obj)

    device = request.COOKIES.get('device')
    fav_items: Favorite = Favorite.objects.filter(device=device)

    context = {
        'obj': obj,
        'fav_items': fav_items,
        'hours': hours
    }
    return render(request, 'restaurant/favorites.html', context)

def add_favorites_view(request, pk):
    device = request.COOKIES.get('device')
    item_id = request.GET.get('id')
    is_checked = request.GET.get('is_checked')
    delete_fav = request.GET.get('delete')

    restaurant = get_object_or_404(Restaurant, cust_pk=pk)
    favorites: Favorite = Favorite.objects.filter(restaurant=pk, device=device)

    response_data = {}   

    if is_checked == 'true':
        Favorite.objects.create(
            device=device,
            item_id=item_id,
            restaurant=restaurant
        )
    elif is_checked == 'false':
        favorite_item = Favorite.objects.filter(device=device, item=item_id)
        favorite_item.delete()

    if delete_fav == 'true':
        get_object_or_404(Favorite, id=item_id).delete()

    response_data['fav_count'] = favorites.count()

    return JsonResponse(response_data)