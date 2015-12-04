
# Nirvaris Profile

A simple Django app to create a user profile using Django authentication.
The app has custom interface for sign in, register, forgot password, activation, edit user details and so.

It uses the follow dependecies from Nirvaris:

- [Nirvaris Default Theme](https://github.com/nirvaris/nirvaris-theme-default)
- [Nirvaris Style Snippet](https://github.com/nirvaris/nirvaris-theme-default)


# Quick start
-

- Django admin must be installed, of course, and you have to run migrate. The app itself does not have any models.

- You can use pip from git to install it. A requirements file is provided with some dependencies.

```
pip install git+https://github.com/nirvaris/nirvaris-profile

```

- Add the _n\_profile_, and its dependencies, to your INSTALLED_APPS:
 
```python
    INSTALLED_APPS = (
        ...
        'n_profile',
        'stylesnippet',
        'themedefault',
    )
```

- As it sends emails for account activation and forgot password, you have to setup your SMTP details in your settings. [Django docs for sending emails](https://docs.djangoproject.com/en/1.9/topics/email/)

```
EMAIL_HOST = ''
EMAIL_PORT = 465
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = True
EMAIL_FROM = ''
```
- There are a few variables to your settings.

```
SITE_URL = 'http://localhost:800' 
AFTER_LOGIN_URL = 'profile-dashboard'
LOGIN_URL = 'login'
MAX_TOKEN_DAYS = 10 #The limit in days for the activation email to be expired
```
- you have to add the url to your urls file:

```
url(r'^profile/', include('n_profile.urls')),
```
- The app urls are:

```
<your-project-url>/profile/register
<your-project-url>/profile/resend-activation-email
<your-project-url>/profile/activation  #this one expect a parameter P whith the activation token
<your-project-url>/profile/login
<your-project-url>/profile/forgot-password
<your-project-url>/profile/profile-dashboard
<your-project-url>/profile/logout
<your-project-url>/profile/change-password
<your-project-url>/profile/change-user-details
```

