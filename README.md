
# Nirvaris Profile

A simple Django app to create a user profile using Django authentication.
The app has custom interface for sign in, register, forgot password, activation, edit user details and so.

It uses the follow dependeciesm from Nirvaris:

- [Nirvaris Default Theme](https://github.com/nirvaris/nirvaris-theme-default)
- [Nirvaris Style Snippet](https://github.com/nirvaris/nirvaris-theme-default)


# Quick start
-

- Django admin must be installed, of course, and you have to run migrate. The app itself does not have any models.

- You can use pip from git to install it:

```
pip install git+https://github.com/nirvaris/nirvaris-profile
pip install git+https://github.com/nirvaris/nirvaris-theme-default
pip install git+https://github.com/nirvaris/nirvaris-style-snippet
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

- As it sends emails for activation and forgot password, you have to setup your SMTP details in your settings.[Django docs for sending emails](https://docs.djangoproject.com/en/1.9/topics/email/)

```
EMAIL_HOST = ''
EMAIL_PORT = 465
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = True
EMAIL_FROM = ''
```

- you have to add the url to your urls file:

```
url(r'^profile/', include('n_profile.urls')),
```