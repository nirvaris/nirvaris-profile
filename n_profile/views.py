import pdb

from datetime import date, timedelta

from django.contrib.auth import login, logout, authenticate
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.utils.translation import ugettext as _
from django.views.generic.base import View, TemplateView, RedirectView
from django.views.generic.edit import FormView

from .crypto import decrypt
from .email import send_activation_email, send_new_password
from .forms import RegisterForm, ResendActivationEmailForm, LoginForm, ForgotPasswordForm, ChangeUserPasswordForm, ChangeUserDetailsForm


# Create your views here.

AFTER_LOGIN_URL = 'profile-dashboard'
LOGIN_URL = 'login'
MAX_TOKEN_DAYS = 10

if hasattr(settings, 'PROFILE_AFTER_LOGIN_URL'):
    if settings.PROFILE_AFTER_LOGIN_URL:
        AFTER_LOGIN_URL = settings.PROFILE_AFTER_LOGIN_URL

if not hasattr(settings, 'LOGIN_URL'):
    LOGIN_URL = settings.LOGIN_URL
    

if hasattr(settings, 'PROFILE_MAX_TOKEN_DAYS'):
    if settings.PROFILE_MAX_TOKEN_DAYS:
        MAX_TOKEN_DAYS = settings.PROFILE_MAX_TOKEN_DAYS

    
class ChangeUserDetailsView(FormView):
    
    template_name = 'change-user-details.html'
    form_class = ChangeUserDetailsForm
    success_url = 'change-user-details'
    
    def get_initial(self):

        initial = super(ChangeUserDetailsView, self).get_initial()
        
        initial['email'] = self.request.user.email
        initial['username'] = self.request.user.username
        initial['name'] = self.request.user.get_full_name()
        
        return initial
    
    def form_valid(self, form):

        form.save()
        messages.success(self.request,_('New details where saved'))

        return super(ChangeUserDetailsView, self).form_valid(form)
        
    def get_form(self):
        form = super(ChangeUserDetailsView, self).get_form()
        form.instance = self.request.user
        return form

class ChangeUserPasswordView(FormView):
    
    template_name = 'change-password.html'
    form_class = ChangeUserPasswordForm
    success_url = 'logout'
            
    def form_valid(self, form):
        #Translators Message at the changeing password form
        if not self.request.user.check_password(form.cleaned_data['current_password']):
            messages.error(self.request, _('Current password does not match'))
            return super(ChangeUserPasswordView, self).form_invalid(form)
            
        self.request.user.set_password(form.cleaned_data['new_password'])
        self.request.user.save()
        
        return super(ChangeUserPasswordView, self).form_valid(form)
        
    def get_form(self):
        form = super(ChangeUserPasswordView, self).get_form()
        form.instance = self.request.user
        return form

class LogoutView(RedirectView):
    permanent = False
    url = 'login'
    
    def get_redirect_url(self, *args, **kwargs):
        logout(self.request)
        return super(LogoutView, self).get_redirect_url(*args, **kwargs)

class ForgotPasswordView(FormView):
    template_name = 'forgot-password.html'
    form_class = ForgotPasswordForm
    success_url = 'forgot-password'

    def get(self,request):
        logout(request)
        return super(ForgotPasswordView,self).get(request)

    def form_valid(self, form):
        
        user = None
        try:
            user = User.objects.get(email=form.cleaned_data['email'])
        except:
            messages.info(self.request,_('E-mail not registered or profile inactive'))
            return super(ForgotPasswordView, self).form_invalid(form)
        
        if user and user.is_active:
            password = User.objects.make_random_password()
            user.set_password(password)
            user.save()
            send_new_password(self.request, user, password)
            messages.success(self.request,_('We have sent an email with your new password'))
        else:
            messages.info(self.request,_('E-mail not registered or profile inactive'))
                
        return super(ForgotPasswordView, self).form_valid(form)

class DashboardView(TemplateView):
    template_name = 'profile-dashboard.html'

class LoginView(FormView):
    template_name = 'login.html'
    form_class = LoginForm
    success_url = AFTER_LOGIN_URL

    def get(self, request):
        if request.user.is_authenticated():
            return redirect(self.success_url)

        if 'next' in request.GET:
            messages.info(self.request,_('Ooops! You have to login to access this page!'))
        return super(LoginView,self).get(request)
 
    def form_valid(self, form):

        email_or_username = form.cleaned_data['email_or_username']
        password = form.cleaned_data['password']      
          
        user = authenticate(username=email_or_username, password=password)

        if not user:
            try:
                user_to_log = User.objects.get(email=email_or_username)
                user = authenticate(username=user_to_log.username, password=password)
            except:
                # Translators: Error message when logins has failed
                messages.error(self.request, _('Login failed. Username or password does not match.'))
                return super(LoginView, self).form_invalid(form)
                    
        if not user:
            messages.error(self.request, _('Login failed. Username or password does not match.'))
            return super(LoginView, self).form_invalid(form)
                        
        if not user.is_active:
            # Translators: Error message when try to login with an NOT activated acocunt
            messages.error(self.request, _('This account is not activated.'))
            return super(LoginView, self).form_invalid(form)
        
        try:
            login(self.request,user)
        except:
            # Translators: Unespected error authenticating the user at the login form            
            messages.error(self.request, _('Something wrong with yout login.'))
            return super(LoginView, self).form_invalid(form)
                        
        if 'next' in self.request.GET:
            self.success_url = self.request.GET['next']

        return super(LoginView, self).form_valid(form)
        
class ActivationView(View):
    template_name = 'profile-activation.html'

    def get(self, request, token):
        #pdb.set_trace()
        logout(request)

        try:
            msg = decrypt(token).split(',')
        
            d = msg[2].split('-')
            dt = date(int(d[0]), int(d[1]), int(d[2]))

        except:
            messages.error(request, _('There is a problem with your activation key.\n\rGo to <a href="%s">Re-send the activation e-mail</a>') % reverse('resend-activation-email'))
            return render_to_response(self.template_name)
        
        if (date.today() - dt) > timedelta (days=MAX_TOKEN_DAYS):
            # Translators: Error message when the user click on the activation link or his e-mail and it has expired
            messages.info(request, _('Your activation has expired.\n\rGo to <a href="%s">Re-send the activation e-mail</a>') % reverse('resend-activation-email'))
            return render_to_response(self.template_name)

        try:
            
            user = User.objects.get(username=msg[0], email=msg[1])

            if user is None:
                raise User.DoesNotExist

            if not user.is_active:
                user.is_active = True
                user.save()
                # Translators: Success message when the user click on the activation link on his email and his account is then activated
                messages.success(self.request,_('Thank you!\n\rYour account has been activated.\n\rPlease, go to <a href="%s">login</a>') % reverse('login'))
            else:
                messages.info(self.request,_('Your account was already activated.\n\rPlease, go to <a href="%s">login</a>') % reverse('login'))
            
        except User.DoesNotExist:
            # Translators: Error message at the re-send activation email form when the email address is not found
            messages.error(self.request,_('The email address was not found.\n\rPlease, go to <a href="%s">register</a>') % reverse('register'))

        return render_to_response(self.template_name)

class ResendActivationEmailView(FormView):
    template_name = 'resend-activation-email.html'
    form_class = ResendActivationEmailForm
    success_url = 'resend-activation-email'

    def get(self,request):
        logout(request)
        return super(ResendActivationEmailView,self).get(request)

    def form_valid(self, form):

        try:
            if not settings.DEBUG:
                user = User.objects.get(email=form.cleaned_data['email'])
            else:
                try:
                    user = User.objects.filter(email=form.cleaned_data['email'])[0]
                except:
                    raise User.DoesNotExist
                if not user:
                    raise User.DoesNotExist

            if user.is_active:
                # Translators: Message at the re-send activation email form when the user is already active
                messages.info(self.request,_('The email address is already active.\n\rPlease, go to <a href="%s">login</a>') % reverse('login'))
            else:
                send_activation_email(self.request, user)
                # Translators: Message at the re-send activation email form when the activation email is re-sent
                messages.success(self.request, _('We have sent you a fresh activation email.'))

        except User.DoesNotExist:
            # Translators: Error message at the re-send activation email form when the email address is not found
            messages.error(self.request,_('The email address was not found.\n\rPlease, go to <a href="%s">register</a>') % reverse('register'))

        return super(ResendActivationEmailView, self).form_valid(form)

class RegisterView(FormView):
    template_name = 'register.html'
    form_class = RegisterForm
    success_url = 'resend-activation-email'
    

    def get(self,request):
        logout(request)
        return super(RegisterView,self).get(request)
    
    def form_valid(self, form):

        new_user = form.save(commit=False)
        
        try:
            send_activation_email(self.request, new_user)
        except:
            messages.error(self.request, _('We had problems sending you an email. Please check your email address'))
            return super(RegisterView, self).form_invalid(form)
                        
        new_user = form.save()
            
        messages.success(self.request, _('We have sent you an activation email.'))

        return super(RegisterView, self).form_valid(form)
