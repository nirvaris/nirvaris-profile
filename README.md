
#Nirvaris Profile


A simple Django app to create a user profile using Django authentication.
The app has custom interface for sign in, register, forgot password, activation, edit user details and so.

It uses the follow dependecies from Nirvaris:

- [Nirvaris Default Theme](https://github.com/nirvaris/nirvaris-theme-default)

#Quick start


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
```

- Some Django variable used by the app. [Django docs](https://docs.djangoproject.com/en/1.9/ref/settings/#login-url)

```
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
```

- Some Nirvaris specific variables to your settings

```
NV_SITE_URL = 'http://localhost:8000/' # used to assemble the activation link
NV_AFTER_LOGIN_URL = 'profile-dashboard' # Or your own after login page
NV_MAX_TOKEN_DAYS = 10 # The limit in days for the activation email to be expired
NV_EMAIL_FROM = '' # The from email the app will send emails out
NV_SECRET_KEY = '' # This key is used by the crypto module to encrypt and decrypt the activation token.
```
- you have to add the url to your urls file:

```
url(r'^profile/', include('n_profile.urls')),
```
- The app's urls are:

```
<your-project-url>/profile/register
<your-project-url>/profile/resend-activation-email
<your-project-url>/profile/activation  #this one expect a parameter P with the activation token
<your-project-url>/profile/login
<your-project-url>/profile/forgot-password
<your-project-url>/profile/profile-dashboard
<your-project-url>/profile/logout
<your-project-url>/profile/change-password
<your-project-url>/profile/change-user-details
```

