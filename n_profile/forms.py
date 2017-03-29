
from django.conf import settings
from django.contrib.auth.models import User
from django.forms import Form, ModelForm, CharField, PasswordInput, EmailField, TextInput, HiddenInput, ImageField, BooleanField
from django.utils.translation import ugettext as _

class InviteUserForm(Form):
    email = EmailField(required=True, label=_('E-mail address'))

class UserDetailsForm(ModelForm):
    current_password = CharField(required=True, label=_('Type your Password'), max_length=30, widget=PasswordInput())
    name = CharField(required=True, label=_('Full Name'), max_length=200)

    class Meta:
        model = User
        labels = {
                    'new_email': _('Your E-mail')
                }
        fields = ['current_password','name', 'email', 'username']

    def clean(self):

        cleaned_data = super(ChangeUserDetailsForm, self).clean()

        try:
            # Translators: Error message at the register form when the email is already used by anither profile

            if not self.instance.check_password(cleaned_data['current_password']):
                self.add_error('current_password', _('Current password does not match'))

            if User.objects.exclude(id=self.instance.id).filter(email=cleaned_data['email']).exists():
                self.add_error('email', _('Email is already in use.'))

            if User.objects.exclude(id=self.instance.id).filter(username=cleaned_data['username']).exists():
                self.add_error('username', _('Username is already in use.'))

        except:
            if len(self.errors)<=0:
                self.add_error(None, _('One or more fields have an invalid value.'))

        try:

            name = cleaned_data['name']

            first_name = name.split(' ')[0].strip()
            last_name = name.replace(first_name, '').strip()

            self.instance.first_name = first_name
            self.instance.last_name = last_name
        except:
            # Translators: Error message at the register form when the name field is black or invalid
            self.add_error('name', _('Name invalid'))

        return cleaned_data

class UserPhotoForm(Form):
    image_file = ImageField()

    def clean(self):
        cleaned_data = super(UserPhotoForm, self).clean()
        img = cleaned_data['image_file'].image

        if img.size[0]<724 or img.size[1] < 763:
            self.add_error('image_file', _('Your image must be bigger than 724x763'))

        return cleaned_data

class ActivateForm(Form):
    #user_id = forms.CharField(required=True, widget=forms.HiddenInput())
    is_active = BooleanField(required=False)
    is_staff = BooleanField(required=False)

class ChangeUserPasswordForm(ModelForm):

    # Translators: Labels on the change pasword from
    current_password = CharField(required=True, label=_('Current Password'), widget=PasswordInput())
    new_password = CharField(required=True, label=_('New Password'), widget=PasswordInput())
    confirm_new_password = CharField(required=True, label=_('Confirm New Password'), widget=PasswordInput())

    class Meta:
        model = User
        fields = ['current_password','new_password', 'confirm_new_password']

    def clean(self):
        cleaned_data = super(ChangeUserPasswordForm, self).clean()
        # Translators: Error message at the change password form when the two new password fields don't match
        try:

            new_password = cleaned_data['new_password']
            confirm_new_password = cleaned_data['confirm_new_password']
            current_password = cleaned_data['current_password']

            if not self.instance.check_password(current_password):
                self.add_error('current_password', _('Current password does not match'))

            if new_password == current_password:
                self.add_error('new_password', _('New password cannot be the same as de current'))

            if new_password != confirm_new_password:
                self.add_error('confirm_new_password', _('Password does not match or blank'))

            return cleaned_data
        except:
            self.add_error(None, _('Password does not match or blank.'))
            return cleaned_data
    def save(self, commit=True):

        self.instance.set_password(self.cleaned_data['new_password'])
        if commit:
            self.instance.save()
        return self.instance

class ForgotPasswordForm(Form):
    email = EmailField(required=True, label=_('E-mail address'))

    def clean(self):
        cleaned_data = super(ForgotPasswordForm, self).clean()

        if not 'email' in cleaned_data:
            return cleaned_data

        try:
            user = User.objects.get(email=cleaned_data['email'])
            if not user.is_active:
                raise
        except:
            # Translators: Error message at the forgot password form
            self.add_error('email', _('E-mail not registered or profile inactive'))

        return cleaned_data

class LoginForm(Form):

    # Translators: Label at the username or email field on the login form
    email_or_username = CharField(required=True, label=_('E-mail or username'))

    # Translators: Label at the password field on the login form
    password = CharField(required=True, label=_('Password'), widget=PasswordInput())

class RegisterForm(ModelForm):

    # Translators: Labels at the fields on the register form
    confirm_password = CharField(required=True, label=_('Confirm your password'), widget=PasswordInput())
    name = CharField(required=True, label=_('Full name'))
    # email = CharField(required=True, label=_('Your E-mail'))

    class Meta:
        model = User
        widgets = {
            'password': PasswordInput(),
        }

        labels = {
                    'password': _('Type your password'),
                    'email': _('Your E-mail')
                }
        fields = ['name', 'email', 'username', 'password', 'confirm_password']
    def clean(self):

        cleaned_data = super(RegisterForm, self).clean()

        # Translators: Error message at the register form when the two password fields don't match
        try:
            password = cleaned_data['password']
            confirm_password = cleaned_data['confirm_password']

            if password != confirm_password:
                self.add_error('password', _('Password does not match or blank.'))

        except:
            return cleaned_data

        # Translators: Error message at the register form when the email is already used by anither profile
        if User.objects.filter(email=cleaned_data['email']).exists():
            self.add_error('email', _('Email is already in use.'))

        if User.objects.filter(username=cleaned_data['username']).exists():
            self.add_error('username', _('Email is already in use.'))

        try:
            name = cleaned_data['name']

            first_name = name.split(' ')[0].strip()
            last_name = name.replace(first_name, '').strip()

            self.instance.first_name = first_name
            self.instance.last_name = last_name
            self.instance.is_active = False

        except:
            # Translators: Error message at the register form when the name field is black or invalid
            self.add_error('name', _('Name invalid'))


        return cleaned_data

    def save(self, commit=True):

        instance = super(RegisterForm, self).save(commit)
        instance.set_password(self.cleaned_data['password'])
        if commit:
            instance.save()
        return instance

class ResendActivationEmailForm(Form):

    email = EmailField(required=True, label=_('E-mail address'))
    def clean(self):
        cleaned_data = super(ResendActivationEmailForm, self).clean()

        if 'email' in cleaned_data:
            if not User.objects.filter(email=cleaned_data['email']).exists():
                self.add_error('email', _('Email not found.'))

        return cleaned_data
