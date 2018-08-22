import pdb

from datetime import date, timedelta
from io import BytesIO

from PIL import Image

from django.contrib.auth import login, logout, authenticate
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.files.base import ContentFile
from django.urls import reverse
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.views.generic.base import View, TemplateView, RedirectView
from django.views.generic.edit import FormView

from menu.mixins import MenuPermissionsMixin
from menu.permissions import is_admin

from .crypto import decrypt
from .email import send_activation_email, send_new_password, send_invitation_email
from .forms import InviteUserForm, RegisterForm, ResendActivationEmailForm, LoginForm
from .forms import UserDetailsForm, ActivateForm, UserPhotoForm, ForgotPasswordForm, ChangeUserPasswordForm, GroupsForm
from .models import UserPhoto

# Create your views here.


NV_AFTER_LOGIN_URL = 'profile-dashboard'
if hasattr(settings, 'NV_AFTER_LOGIN_URL'):
    if settings.NV_AFTER_LOGIN_URL:
        NV_AFTER_LOGIN_URL = settings.NV_AFTER_LOGIN_URL

LOGIN_URL = 'login'
if not hasattr(settings, 'LOGIN_URL'):
    LOGIN_URL = settings.LOGIN_URL

NV_MAX_TOKEN_DAYS = 20
if hasattr(settings, 'NV_MAX_TOKEN_DAYS'):
    if settings.NV_MAX_TOKEN_DAYS:
        NV_MAX_TOKEN_DAYS = settings.NV_MAX_TOKEN_DAYS


class InvitationView(View):
    template_name = 'invitation.html'

    def get(self, request, token):
        #pdb.set_trace()
        logout(request)

        try:
            #msg = 'invite,' + email + ',' + gs + ',' + due_date.strftime("%Y-%m-%d")

            msg = decrypt(token).split(',')
            request.session['invite_groups'] = msg[2]
            d = msg[3].split('-')
            dt = date(int(d[0]), int(d[1]), int(d[2]))

            if msg[0]!='invite':
                raise Exception(_('It is not a invitation token'))

        except:
            messages.error(request, _('There is a problem with your invitation key.\n\rContact us for more dtails.'))
            return redirect('login')

        if (date.today() - dt) > timedelta (days=NV_MAX_TOKEN_DAYS):
            # Translators: Error message when the user click on the activation link or his e-mail and it has expired
            messages.info(request, _('Your invitation has expired.\n\rContact us for more details.'))
            return redirect('login')

        try:

            if User.objects.filter(email=msg[1]).exists():
                messages.error(self.request,_('This invitation email is already in use.\r\rContact us for more details'))
                return redirect('login')

            form = RegisterForm(initial={'email':msg[1]});
            #request_context = RequestContext(request,{'form':form})
            #return render_to_response(self.template_name, request_context)

            return render(request,self.template_name, {'form':form})

        except:
            # Translators: Error message at the re-send activation email form when the email address is not found
            messages.error(self.request,_('Something went wrong with your invitation.\n\rPlease, contact us') % reverse('register'))

        #return render_to_response(self.template_name)
        return render(request, self.template_name)

    @transaction.atomic
    def post(self, request, token):

        form = RegisterForm(request.POST)
        form_valid = form.is_valid()

        if not form_valid:
            #return render_to_response(self.template_name)
            return render(request,self.template_name)

        form.save()
        form.instance.is_active = True
        form.instance.save()

        if request.session['invite_groups']:
            groups = request.session['invite_groups'].split(';')
            for g in groups:
                if g:
                    gr = Group.objects.get(id=int(g))
                    form.instance.groups.add(gr)
            form.instance.save()

        messages.success(self.request, _('Your account is now created.\r\nPlease, login.'))
        return redirect(settings.LOGIN_URL)


class InviteUserView(LoginRequiredMixin, MenuPermissionsMixin, FormView):
    template_name = 'invite-user.html'
    form_class = InviteUserForm
    success_url = 'invite-user'

    def dispatch(self, request, *args, **kwargs):
        #pdb.set_trace()
        user = self.request.user
        if not user.is_superuser and not is_admin(user):
                raise PermissionDenied

        return super(InviteUserView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):

        email = form.cleaned_data['email']
        groups = form.cleaned_data['groups']

        if User.objects.filter(email=email).exists():
            messages.error(self.request, _('Email address already activated by a user.'))
            return super(InviteUserView, self).form_valid(form)

        send_invitation_email(self.request,  email, groups)

        messages.success(self.request,_('We have sent the invitation email.'))

        return super(InviteUserView, self).form_valid(form)

class UserDetailsView(LoginRequiredMixin, View):
    template_name = 'user-details.html'

    def dispatch(self, request, *args, **kwargs):
        #pdb.set_trace()
        user = self.request.user
        if not user.is_superuser and not is_admin(user):
                raise PermissionDenied

        return super(UserDetailsView, self).dispatch(request, *args, **kwargs)

    def get(self, request, user_id):
        #pdb.set_trace()
        user_seen = User.objects.get(id=user_id)

        data_context = {}
        data_context['user_details'] = user_seen
        data_context['form_activate'] = ActivateForm(initial={'is_active':user_seen.is_active})

        users_groups = []
        for g in user_seen.groups.all():
            users_groups.append(g.id)

        form_groups = GroupsForm(initial = {'groups':users_groups})
        data_context['form_groups'] = form_groups

        return render(request,self.template_name, data_context)

    def post(self, request, user_id):

        if request.user.id==int(user_id):
            messages.error(self.request, _('Oooops! You cannot change your own permissions!'))
            data_context = {}
            user_seen = User.objects.get(id=user_id)
            data_context['user_details'] = user_seen
            data_context['form_activate'] = ActivateForm(initial={'is_active':user_seen.is_active})
            users_groups = []
            for g in user_seen.groups.all():
                users_groups.append(g.id)

            form_groups = GroupsForm(initial = {'groups':users_groups})
            data_context['form_groups'] = form_groups

            return render(request,self.template_name, data_context)

        action = request.POST['action']

        if action == 'form_activation':

            form_activate = ActivateForm(self.request.POST)
            form_valid = form_activate.is_valid()

            user_seen = User.objects.get(id=user_id)

            if form_valid:
                user_seen.is_active = form_activate.cleaned_data['is_active']

                user_seen.save()
                messages.success(self.request, _('User permisions changed!'))

            data_context = {}
            data_context['user_details'] = user_seen
            data_context['form_activate'] = form_activate

            users_groups = []
            for g in user_seen.groups.all():
                users_groups.append(g.id)

            form_groups = GroupsForm(initial = {'groups':users_groups})
            data_context['form_groups'] = form_groups

            return render(request,self.template_name, data_context)


        if action == 'form_groups':

            user_seen = User.objects.get(id=user_id)
            form_groups = GroupsForm(request.POST)
            if form_groups.is_valid():
                for group in Group.objects.all():
                    if str(group.id) in form_groups.cleaned_data['groups']:
                        user_seen.groups.add(group)
                    else:
                        user_seen.groups.remove(group)

                user_seen.save()

            data_context = {}

            data_context['user_details'] = user_seen
            data_context['form_activate'] = ActivateForm(initial={'is_active':user_seen.is_active})
            users_groups = []
            for g in user_seen.groups.all():
                users_groups.append(g.id)

            form_groups = GroupsForm(initial = {'groups':users_groups})
            data_context['form_groups'] = form_groups

            return render(request,self.template_name, data_context)

class UsersListView(LoginRequiredMixin, MenuPermissionsMixin, View):
    template_name = 'users-list.html'

    def get(self, request):

        data_context = {}
        data_context['users_list'] = User.objects.all()
        return render(request,self.template_name, data_context)

class UserProfileView(LoginRequiredMixin, View):

    template_name = 'user-profile.html'

    def get(self, request):
        #pdb.set_trace()
        user = self.request.user

        initial = {}
        initial['email'] = user.email
        initial['name'] = user.get_full_name()
        initial['username'] = user.username

        form_details = UserDetailsForm(instance=user, initial=initial)

        data_context = {}
        data_context['form_details'] = form_details
        data_context['form_photo'] = UserPhotoForm()

        return render(request,self.template_name, data_context)

    def post(self, request):

        action = request.POST['action']
        user = self.request.user

        if action == 'form_details':
            form_details = UserDetailsForm(request.POST)
            form_details.instance = user

            try:

                form_details.save()
                messages.success(self.request, _('User\'s details were saved!!'))

            except:
                ...

            data_context = {}
            data_context['form_details'] = form_details
            data_context['form_photo'] = UserPhotoForm()

            return render(request,self.template_name, data_context)

        if action == 'form_photo':

            form_photo = UserPhotoForm(request.POST, request.FILES)
            form_valid = form_photo.is_valid()
            if form_valid:

                if UserPhoto.objects.filter(user=user).exists():
                    user_photo = UserPhoto.objects.get(user=user)
                else:
                    user_photo = UserPhoto(user=user)

                #pdb.set_trace()
                img = Image.open(request.FILES['image_file'])

                photo_name = request.FILES['image_file'].name.split('/')[-1]
                ext = photo_name.split('.')[-1]

                size = (724,763)
                img_724 = img.copy()
                img_724.thumbnail(size)
                img_724_name = photo_name.replace(ext, '') + 'thumb_724.' + ext

                f = BytesIO()
                img_724.save(f, format=img.format)
                user_photo.photo.save(img_724_name,ContentFile(f.getvalue()))
                f.close()

                size = (350,350)
                img_350 = img.copy()
                img_350.thumbnail(size)
                img_350_name = photo_name.replace(ext, '') + 'thumb_350.' + ext

                f = BytesIO()
                img_350.save(f, format=img.format)
                user_photo.photo_350.save(img_350_name,ContentFile(f.getvalue()))
                f.close()

                size = (40,40)
                img_40 = img.copy()
                img_40.thumbnail(size)
                img_40_name = photo_name.replace(ext, '') + 'thumb_40.' + ext

                f = BytesIO()
                img_40.save(f, format=img.format)
                user_photo.photo_40.save(img_40_name,ContentFile(f.getvalue()))
                f.close()

                user_photo.save()

            initial = {}
            initial['email'] = user.email
            initial['name'] = user.get_full_name()
            initial['username'] = user.username

            form_details = UserDetailsForm(instance=user, initial=initial)

            data_context = {}
            data_context['form_details'] = form_details
            data_context['form_photo'] = form_photo

            return render(request,self.template_name, data_context)

        return render(request,self.template_name)

class ChangeUserPasswordView(LoginRequiredMixin, FormView):

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

class DashboardView(LoginRequiredMixin, MenuPermissionsMixin, TemplateView):
    template_name = 'profile-dashboard.html'

class LoginView(FormView):
    template_name = 'login.html'
    form_class = LoginForm
    success_url = NV_AFTER_LOGIN_URL

    def get(self, request):
        if request.user.is_authenticated:
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
            #return render_to_response(self.template_name)
            return render(request,self.template_name)

        if (date.today() - dt) > timedelta (days=NV_MAX_TOKEN_DAYS):
            # Translators: Error message when the user click on the activation link or his e-mail and it has expired
            messages.info(request, _('Your activation has expired.\n\rGo to <a href="%s">Re-send the activation e-mail</a>') % reverse('resend-activation-email'))
            #return render_to_response(self.template_name)
            return render(request,self.template_name)

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

        #return render_to_response(self.template_name)
        return render(request,self.template_name)

class ResendActivationEmailView(MenuPermissionsMixin, FormView):
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

class RegisterView(MenuPermissionsMixin, FormView):
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
