from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .forms import UserCreateForm
from pages.forms import RestaurantForm
from formtools.wizard.views import SessionWizardView
from allauth.account.utils import complete_signup
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from pages.decorators import unauthenticated_user
from django.contrib import messages
from django.conf import settings
from restaurant.models import Restaurant, RestaurantHours
from .models import SignUpCode

# Create your views here.
User = get_user_model()

FORMS = [("signup", UserCreateForm),
         ("restaurant", RestaurantForm)]

TEMPLATES = {'signup': 'account/signup.html',
             'restaurant': 'account/restaurant.html'}

class FormWizardView(SessionWizardView):
    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]
    
    @method_decorator(unauthenticated_user)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def done(self, form_list, **kwargs):


        try:
            form_dict = self.get_all_cleaned_data()
            signupcode = form_dict['signup_code']
            code_query = SignUpCode.objects.get(signup_code__exact=signupcode)

            if signupcode == code_query.signup_code:
                for form in form_list:
                    if isinstance(form, UserCreateForm):
                        user = form.save(self.request)     
                        complete_signup(self.request, user, settings.ACCOUNT_EMAIL_VERIFICATION, settings.LOGIN_REDIRECT_URL)

                        code_query.delete()
                    elif isinstance(form, RestaurantForm):

                        restaurant_name = form.cleaned_data['name']
                        address1 = form.cleaned_data['address1']
                        address2 = form.cleaned_data['address2']
                        city = form.cleaned_data['city']
                        state  = form.cleaned_data['state']
                        zipcode = form.cleaned_data['zipcode']

                        user = self.request.user
                        
                        restaurant = Restaurant.objects.create(owner=user, name=restaurant_name, address1=address1, address2=address2, city=city, state=state, zipcode=zipcode)
                        RestaurantHours.objects.create(restaurant=restaurant)
                return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
        except SignUpCode.DoesNotExist:
            return HttpResponse("Invalid sign up code.")
        
        

# def login_view(request):
#     if request.user.is_authenticated:
#         return redirect('dashboard')
#     else:
#         if request.method == 'POST':
#             username = request.POST.get('username')
#             password = request.POST.get('password')
#             user = authenticate(request, username=username, password=password)

#             if user is not None:
#                 login(request, user)
#                 return redirect('dashboard')
#             else:
#                 messages.info(request, "Username or password is incorrect.")

#         context = {}
#         return render(request, 'users/login.html', context)

# def logout_view(request):
#     logout(request)
#     return redirect('account_login')