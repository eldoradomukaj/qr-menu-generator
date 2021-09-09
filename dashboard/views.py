from collections import defaultdict
from datetime import date, datetime, time, timedelta
from random import randint
from typing import Any, Callable, Dict, Set, Union

from django.apps import apps
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import MenuForm, CategoryForm, RestaurantUpdateForm, CategoryFormUpload, RestaurantHoursUpdateForm
from pages.forms import RestaurantForm
from restaurant.models import Restaurant, Category, RestaurantHours, SpecialDays, Order, OrderItem, Menu
import json
from django.db.models import F
from django.db import IntegrityError

from django.core import serializers
from opensimplex import OpenSimplex


# Create your views here.

@login_required(login_url='account_login')
def dashboard(request):
    restaurant = get_object_or_404(Restaurant, owner=request.user)
    menu_items = Menu.objects.filter(user=request.user).count()
    category_items = Category.objects.filter(restaurant=restaurant).count()
    owner_restaurant = Restaurant.objects.filter(owner=request.user)
    orders = Order.objects.filter(restaurant=restaurant)
    context = {
        'dashboard_page': 'active',
        'menu_items': menu_items,
        'category_items': category_items,
        'url': request.get_host,
        'restaurant': owner_restaurant,
        'orders': orders,
    }
    return render(request, 'dashboard/index.html', context)


@login_required(login_url='account_login')
def analytics_data(request) -> Union[HttpResponse, JsonResponse]:
    def get_color(itemIdx: int, numItems: int, alpha: int = 1) -> str:
        if (numItems - 1) == 0: return 'rgba(234, 121, 185, {})'.format(alpha)
        delta: float = itemIdx / (numItems - 1)
        return 'rgba({}, {}, {}, {})'.format(
            round(234 - (delta * 211)),
            round(121 + (delta * 40)),
            round(185 + (delta * 37)),
            alpha
        )

    if not request.is_ajax():
        return HttpResponse("Nothing to see here.")

    owner_restaurant: Restaurant = Restaurant.objects.get(owner=request.user)
    data_type: str = request.GET.get('type', 'categories')
    date_filter: str = request.GET.get('range', 'week')
    category_filter: Union[str, None] = request.GET.get('category', None)

    date_range_delta: int = {
        'week': 7,
        'month': 30,
        'year': 365,
    }[date_filter]
    date_range_format: str = {
        'week': '%A',
        'month': '%m/%d',
        'year': '%m/%d',
    }[date_filter]

    datasets: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
        'data': {(datetime.combine(date.today(), time()) - timedelta(days=n)).date(): 0 for n in range(date_range_delta)},
        'fill': 'origin',
    })
    cat_set: Set[str] = set()

    # get data from Google
    if owner_restaurant.is_demo:
        base_int: int = randint(400, 600)
        divisor: float = {
            'week': 1,
            'month': 1 / 8,
            'year': 1 / 80,
        }[date_filter]

        if data_type == 'categories':
            categories: List[Category] = Category.objects.filter(restaurant=owner_restaurant)
            for category in categories:
                noise: OpenSimplex = OpenSimplex(randint(0, 1073741824))
                i: int = 5
                for d in datasets[category.cat_name]['data'].keys():
                    datasets[category.cat_name]['data'][d] = int(base_int + (80 * noise.noise2d(i * divisor, 0)))
                    i += 1
        else:  # menus
            cat_set = set(Category.objects.filter(restaurant=owner_restaurant))
            menus: List[Menu] = Menu.objects.filter(owner=owner_restaurant)
            for menu in menus:
                if category_filter and category_filter != "Any":
                    if menu.category.cat_name != category_filter: continue
                
                noise: OpenSimplex = OpenSimplex(randint(0, 1073741824))
                i: int = 5
                for d in datasets[menu.title]['data'].keys():
                    datasets[menu.title]['data'][d] = int(base_int + (80 * noise.noise2d(i * divisor, 0)))
                    i += 1
    else:
        analytics = apps.get_app_config('dashboard').analytics
        analytics_data = analytics.reports().batchGet(
            body={
                'reportRequests': [
                {
                    'viewId': settings.GCP_VIEW_ID,
                    'dateRanges': [{
                        'startDate': (datetime.combine(date.today(), time()) - timedelta(days=date_range_delta)).strftime("%Y-%m-%d"),
                        'endDate': 'today'
                    }],
                    'metrics': [{'expression': 'ga:pageviews'}],
                    'dimensionFilterClauses': [{
                        'filters': [{
                            'dimensionName': 'ga:pagePath',
                            'operator': 'REGEXP',
                            'expressions': [r'\A\/restaurant\/{}*'.format(str(owner_restaurant.cust_pk))]
                        }],
                    }],
                    'dimensions': [
                        {'name': 'ga:pagePath'},
                        {'name': 'ga:dateHourMinute'},
                    ]
                }],
            }
        ).execute()
        report = analytics_data.get('reports', [None])[0].get('data', {}).get('rows', [])

        # build JSON output from analytics data
        if report is not None:
            for row in report:
                url: str
                timestamp: str
                url, timestamp = row['dimensions']
                hits: str = row['metrics'][0]['values'][0]

                this_date: date = datetime.strptime(timestamp, "%Y%m%d%H%M").date()

                url_broken = url.lstrip('/').rstrip('/').split('/')[1:]
                if data_type == 'categories' and len(url_broken) == 2:
                    if url_broken[1].lower() == "order":
                        continue
                    
                    try:
                        viewed_cat: Category = Category.objects.get(slug=url_broken[1])
                        datasets[viewed_cat.cat_name]['data'][this_date] += int(hits)
                    except Category.DoesNotExist:
                        continue
                elif data_type == 'items' and len(url_broken) == 3:
                    try:
                        viewed_menu: Menu = Menu.objects.get(id=int(url_broken[2]))
                        cat_set.add(viewed_menu.category)
                        if category_filter and category_filter != "Any":
                            if viewed_menu.category.cat_name != category_filter:
                                continue
                        datasets[viewed_menu.title]['data'][this_date] += int(hits)
                    except Menu.DoesNotExist:
                        continue

    # prep our outgoing JSON object
    max_size: int = 0
    min_size: int = 100000
    for key, dataset in datasets.items():
        # group by week for year view
        if date_filter == 'year':
            new_data: Dict[date, int] = defaultdict(lambda: 0)
            for d, v in dataset['data'].items():
                start_of_week: date = (datetime.combine(d, time()) - timedelta(days=d.weekday())).date()
                new_data[start_of_week] += v
            dataset['data'] = new_data

        max_size = max(max_size, max(dataset['data'].values()))
        min_size = min(min_size, min(dataset['data'].values()))
        dataset['data'] = [{'x': d.strftime("%Y-%m-%d"), 'y': v} for d, v in dataset['data'].items()]
        if date_filter == 'year': dataset['data'] = dataset['data'][1:-1]
        dataset['label'] = key

    y_max: int = max(round(max_size * 1.05), max_size + 1)
    y_min: int = max(round(min_size * 0.95), 0)

    analytics_out: dict = {
        'options': {
            'max': y_max,  # add whitespace above max chart value
            'min': y_min,
            'precision': 0,
            'weekLabels': date_filter == 'year',  # prepend "Week of" to tooltip title
            'hiding': len(datasets) > 10,
        },
        'datasets': sorted([i for i in datasets.values()], key=lambda d: sum([i['y'] for i in d['data']]))[:10],
    }
    
    counter: int = 0
    for ds in analytics_out['datasets']:
        ds['backgroundColor'] = get_color(counter, len(analytics_out['datasets']), 0.2)
        ds['borderColor'] = get_color(counter, len(analytics_out['datasets']))
        counter += 1

    if not category_filter or category_filter == "Any":
        # unused keys get ignored by Chart.js, so we can dump it into the data object
        analytics_out["categories"] = [c.cat_name for c in cat_set]

    return JsonResponse(analytics_out)

@login_required(login_url='account_login')
def account_update_view(request):

    return render(request, 'dashboard/account_edit.html', context)

@login_required(login_url='account_login')
def create_menu(request):
    form = MenuForm()
    category_form = CategoryForm()

    if request.method == 'POST':
        form = MenuForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data.get('title')
            price = form.cleaned_data.get('price')
            description = form.cleaned_data.get('description')
            image = form.cleaned_data.get('image')
            category = request.POST.get('category')

            Menu.objects.create(title=title, price=price, description=description, image=image, category=category, user=request.user, owner=Restaurant.objects.get(owner=request.user))


            messages.success(request, "Form saved successfully.")
            form = MenuForm()
    else:
        print(form.errors)

    menu = Menu.objects.filter(user=request.user).order_by('category', 'title')

    categories = Category.objects.filter(restaurant=Restaurant.objects.get(owner=request.user)).order_by('position')

    context = {
        'managemenu_page': 'active',
        'cat_form': category_form,
        'form': form,
        'menu': menu,
        'categories': categories
    }
    return render(request, 'dashboard/createmenu.html', context)

@login_required(login_url='account_login')
def create_category(request):
    category_form = CategoryForm()

    cat_name = request.POST.getlist('cat_name') or None
    restaurant = get_object_or_404(Restaurant, owner=request.user)
    
    try:
        if request.method == 'POST':
            category_form = CategoryForm(request.POST)
            if category_form.is_valid():
                #cat_name = request.POST.getlist('cat_name')
                
                count = 0
                for cat in cat_name:
                    count += 1
                    if cat == "" and count == 1:
                        messages.error(request, 'Please enter at least one category')
                    elif cat != '':
                        Category.objects.create(cat_name=cat, restaurant=restaurant)
                        messages.success(request, "Category created successfully")
                
                category_form = CategoryForm()

                return HttpResponseRedirect(reverse('managemenu'))
            else:
                messages.error(request, 'Unable to create category')
    except IntegrityError:
        messages.error(request, "Category already exists")
    

    categories = Category.objects.filter(restaurant=Restaurant.objects.get(owner=request.user)).order_by('position')

    context = {
        'cat_form': category_form,
        'categories': categories,
        'restaurant': restaurant,
        'category_page': 'active'
    }
    return render(request, 'dashboard/category.html', context)

@login_required(login_url='account_login')
def add_by_category_view(request, id):
    menu_item = Menu.objects.filter(user=request.user, category__slug=id).order_by('-image', '-image_url', 'title' )
    restaurant = Restaurant.objects.get(owner=request.user)
    category: Category = Category.objects.filter(restaurant=restaurant, slug=id)

    form = MenuForm()

    if request.method == 'POST':
        form = MenuForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data.get('title')
            price = form.cleaned_data.get('price')
            units = form.cleaned_data.get('units')
            custom_unit = form.cleaned_data.get('custom_unit')
            description = form.cleaned_data.get('description')
            image = form.cleaned_data.get('image')
            image_url = form.cleaned_data.get('image_url')
            allergens = form.cleaned_data.get('allergens')

            Menu.objects.create(
                title=title,
                price=price,
                units=units,
                custom_unit=custom_unit,
                description=description,
                image_url=image_url,
                image=image,
                allergens=allergens,
                category=category[0],
                user=request.user,
                owner=restaurant)
            messages.success(request, "Form saved successfully.")
            form = MenuForm()
            return HttpResponseRedirect(reverse('category-add', args=(id,)))
        else:
            messages.error(request, "Unable to create menu item")
    else:
        pass
        #messages.error(request, "Something went wrong")

    context = {
        'menu_item': menu_item,
        'category': category,
        'form': form
    }
    return render(request, 'dashboard/category_manage.html', context)


@login_required(login_url='account_login')
def menu_item_delete_view(request, pk):
    menu_item = get_object_or_404(Menu, user=request.user, id=pk)

    if request.method == 'POST':
        if menu_item.image:
            menu_item.image.delete()
        menu_item.delete()
        return HttpResponseRedirect(reverse('managemenu'))

    context = {
        'item': menu_item
    }
    return render(request, 'dashboard/delete_menu_item.html', context)

@login_required(login_url='account_login')
def menu_item_update_view(request, pk):
    restaurant = Restaurant.objects.get(owner=request.user)
    categories = Category.objects.filter(restaurant=restaurant)

    current_category = Menu.objects.filter(id=pk)

    menu_item = get_object_or_404(Menu, user=request.user, id=pk)
    menu_form = MenuForm(instance=menu_item)

    if request.method == 'POST':
        menu_form = MenuForm(request.POST, request.FILES, instance=menu_item)
        if menu_form.is_valid():
            category = request.POST.get('category')
            
            menu_form.save()
            Menu.objects.filter(id=pk).update(category=category)

            return HttpResponseRedirect(reverse('managemenu'))

    context = {
        'menu_form': menu_form,
        'category': categories,
        'current_category': current_category
    }
    return render(request, 'dashboard/update_menu_item.html', context)

@login_required(login_url='account_login')
def qrcode_view(request):

    owner_restaurant = Restaurant.objects.filter(owner=request.user)

    context = {
        'qrcode_page': 'active',
        'url': request.get_host,
        'restaurant': owner_restaurant
    }
    return render(request, 'dashboard/qrcode.html', context)

@login_required(login_url='account_login')
def restaurant_info(request):

    restaurant = Restaurant.objects.get(owner=request.user)
    hours = RestaurantHours.objects.get(restaurant=restaurant)

    context = {
        'restaurant_page': 'active',
        'restaurant': restaurant,
        'days': [
            "Monday: " + (hours.monday_hours if hours.monday else "Closed"),
            "Tuesday: " + (hours.tuesday_hours if hours.tuesday else "Closed"),
            "Wednesday: " + (hours.wednesday_hours if hours.wednesday else "Closed"),
            "Thursday: " + (hours.thursday_hours if hours.thursday else "Closed"),
            "Friday: " + (hours.friday_hours if hours.friday else "Closed"),
            "Saturday: " + (hours.saturday_hours if hours.saturday else "Closed"),
            "Sunday: " + (hours.sunday_hours if hours.sunday else "Closed"),
        ],
    }
    return render(request, 'dashboard/restaurant.html', context)

@login_required(login_url='account_login')
def item_detail(request, pk):
    obj = Menu.objects.get(id=pk)
    
    context = {
        'obj': obj
    }
    return render(request, 'dashboard/test.html', context)

@login_required(login_url='account_login')
def account_view(request):
    
    context = {}
    return render(request, 'dashboard/account.html', context)

@login_required(login_url='account_login')
def delete_mult_menu_items(request):
    chk = request.POST.getlist('menu-items')
    dropdown = request.POST.get('menu-dropdown')

    if request.method == 'POST':
        if dropdown == 'delete-item':
            Menu.objects.filter(id__in=chk).delete()
    return HttpResponseRedirect(reverse('managemenu'))

@login_required(login_url='account_login')
def category_update_view(request):

    pk = request.POST.get('pk')
    obj = get_object_or_404(Category, pk=pk)

    form = CategoryFormUpload(instance=obj)

    context = {
        'obj': obj,
        'form': form
    }
    return render(request, 'dashboard/category_update_modal.html', context)


@login_required(login_url='account_login')
def save_category_update_view(request, pk):
    obj = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        form = CategoryFormUpload(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            obj.save()

            messages.success(request, "Category updated sucessfully")
            
            return HttpResponseRedirect(reverse('managemenu'))
    else:
        messages.error(request, "Unable to save item")
        return HttpResponseRedirect(next)
    

@login_required(login_url='account_login')
def set_menu_hidden_view(request, pk):
    response_data = {}
    
    toggleinfo = request.GET.get('menutoggle')
    response_data['value'] = toggleinfo
    chk_val = response_data['value']
    

    if chk_val is None:
        Menu.objects.filter(id=pk).update(is_shown=False)

    else:
        Menu.objects.filter(id=pk).update(is_shown=True)
    return JsonResponse(response_data)

@login_required(login_url='account_login')
def update_position_view(request, pk):

    response_data = {}

    query = Category.objects.filter(id=pk)
 
    if request.is_ajax():
        position = request.GET.get('position')
        prev_card = request.GET.get('prev')
        next_card = request.GET.get('next')
        prev_pk = request.GET.get('prev_pk')
        next_pk = request.GET.get('next_pk')
        
        query_prev = Category.objects.filter(id=prev_pk)
        query_next = Category.objects.filter(id=next_pk)

        query.update(position=position)

        if query_next:
            query_next.update(position=next_card)
        if query_prev:
            query_prev.update(position=prev_card)
        
        return JsonResponse(response_data)
    else:
        return HttpResponse('Nothing to see here.')
    
@login_required(login_url='account_login')
def restaurant_update_view(request):
    restaurant_info = get_object_or_404(Restaurant, owner=request.user)
    hours = get_object_or_404(RestaurantHours, restaurant=restaurant_info)

    restaurant_form = RestaurantUpdateForm(instance=restaurant_info, prefix="restaurant")
    hours_form = RestaurantHoursUpdateForm(instance=hours, prefix="hours")

    if request.method == 'POST':
        restaurant_form = RestaurantUpdateForm(request.POST, request.FILES, instance=restaurant_info, prefix="restaurant")
        hours_form = RestaurantHoursUpdateForm(request.POST, instance=hours, prefix="hours")
        
        if restaurant_form.is_valid() and hours_form.is_valid():
            restaurant_form.save()
            hours_form.save()
            messages.success(request, "Restaurant information updated successfully")

            return HttpResponseRedirect(reverse('restaurant'))
        else:
            messages.error(request, "Unable to update information")


    context = {
        'restaurant_form': restaurant_form,
        'hours_form': hours_form,
        'restaurant_info': restaurant_info
    }
    return render(request, 'dashboard/restaurant_update.html', context)

@login_required(login_url='account_login')
def delete_menu_item(request, pk):
    response_data = {}
    query = get_object_or_404(Menu, id=pk)

    value = request.POST.get('value')
    response_data['value'] = value

    if request.method == 'POST' and request.is_ajax():
        query.delete()

    return JsonResponse(response_data)

@login_required(login_url='account_login')
def delete_cat_item(request, pk):
    response_data = {}
    query = get_object_or_404(Category, id=pk)

    value = request.POST.get('value')
    response_data['value'] = value

    if request.method == 'POST' and request.is_ajax():
        query.delete()

    return JsonResponse(response_data)

@login_required(login_url='account_login')
def load_menu_item(request):
    
    pk = request.POST.get('pk')
    
    obj = get_object_or_404(Menu, pk=pk)
    cat = Menu.objects.filter(pk=pk)

    form = MenuForm(instance=obj)

    context = {
        'cat': cat, 
        'object': obj,
        'pk': pk,
        'form': form 
    }
    return render(request, 'dashboard/update_menu_modal.html', context)

@login_required(login_url='account_login')
def update_menu_item(request, pk):
    obj = get_object_or_404(Menu, pk=pk)

    if request.method == 'POST':
        form = MenuForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()

            messages.success(request, "Item updated sucessfully")
            next = request.POST.get('next')
            return HttpResponseRedirect(next)
    else:
        messages.error(request, "Unable to save item")
        return HttpResponseRedirect(next)

@login_required(login_url='account_login')        
def hide_category_view(request):
    response_data = {}
    checkbox_id = request.POST.get('id')
    is_checked = request.POST.get('is_checked')
    query = Category.objects.filter(pk=checkbox_id)

    if request.method == 'POST' and request.is_ajax():
        if is_checked == 'true':
            query.update(is_shown=True)
        elif is_checked == 'false':
            query.update(is_shown=False)
    
    return JsonResponse(response_data)

@login_required(login_url='account_login')
def fetch_orders_view(request):
    
    try:
        restaurant = Restaurant.objects.get(owner=request.user)
        orders = list(Order.objects.filter(restaurant=restaurant).exclude(order_status='').order_by('-date_ordered').values())
    
    except Restaurant.DoesNotExist:
        return HttpResponse('does not exist')

    data = dict()
    data['orders'] = orders


    return JsonResponse(data)

@login_required(login_url='account_login')
def publish_menu_view(request):
    response_data = {}

    data_pk = request.GET.get('pk')
    is_checked = request.GET.get('is_checked')

    if request.is_ajax():
        query = Restaurant.objects.filter(owner=request.user, pk=data_pk)
        
        if is_checked == 'true':
            query.update(is_live=True)
        elif is_checked == 'false':
            query.update(is_live=False)

    return JsonResponse(response_data)

@login_required(login_url='account_login')
def remove_image_view(request):
    response_data = {}
    restaurant_pk = request.GET.get('id')

    check_owner: Restaurant = get_object_or_404(Restaurant, cust_pk=restaurant_pk)
    query: Restaurant = Restaurant.objects.filter(cust_pk=restaurant_pk)
    
    if request.is_ajax() and request.user == check_owner.owner:
        query.update(rest_logo="")
    
    return JsonResponse(response_data)


@login_required(login_url='account_login')
def remove_menu_item_image(request):
    response_data = {}
    restaurant_owner: Restaurant = Restaurant.objects.get(owner=request.user)
    menu_pk = request.GET.get('id')
    query: Menu = Menu.objects.filter(owner=restaurant_owner, id=menu_pk)

    if request.is_ajax():
        query.update(image="")

    return JsonResponse(response_data)