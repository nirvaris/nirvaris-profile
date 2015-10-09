=====
Nirvaris Pages
=====

A simple Django app to create a user profile and custom authentication, sign in, forgot password and so on.

Quick start
-----------

To install the Profile, use pip from git:

pip install git+https://github.com/nirvaris/nirvaris-profile

1. Add "profile" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'n_profile',
    )

2. You have to run makemigrations and migrate, as it uses Django authentication

3. You can copy the templates on the app's template folder to your application template folders, so you can style your own.
	
4. you have to add the url to your urls file:  url(r'^profile/', include('profile.urls')),