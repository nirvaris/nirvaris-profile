from django.contrib.auth.models import User
from django.test import TestCase

from .commons import create_user_jack, create_user_james
from ..forms import RegisterForm, ChangeUserPasswordForm, ChangeUserDetailsForm, ResendActivationEmailForm, ForgotPasswordForm, LoginForm

class ProfileFormsTestCase(TestCase):
    
    def setUp(self):
        ...
    def tearDown(self):
        ...

    def test_login(self):
        
        form = LoginForm(data={'email_or_username':'jack','password':'pas'})
        self.assertTrue(form.is_valid())
        
        form = LoginForm(data={'email_or_username':'jack@awesome.com','password':'pas'})
        self.assertTrue(form.is_valid())

        form = LoginForm(data={'email_or_username':'','password':''})
        self.assertFalse(form.is_valid())
        
    def test_forgot_password(self):
 
        jack_user = create_user_jack()
        # non active jack
        form = ForgotPasswordForm(data={'email':'jack@awesome.com'})
        self.assertFalse(form.is_valid())
        
        #active jack
        jack_user.is_active = True
        jack_user.save()
        
        form = ForgotPasswordForm(data={'email':'jack@awesome.com'})
        self.assertTrue(form.is_valid())
 
        # it is not jack's email
        form = ForgotPasswordForm(data={'email':'not-jack@awesome.com'})
        self.assertFalse(form.is_valid())
     
    def test_resend_activation_email(self):
        
        jack_user = create_user_jack(True)
        
        form = ResendActivationEmailForm(data={'email':'jack@awesome.com'})
        self.assertTrue(form.is_valid())
        
        form = ResendActivationEmailForm(data={'email':'not-jack@awesome.com'})
        self.assertFalse(form.is_valid())
        
    def test_change_details(self):
    
        
        jack_user = create_user_jack(True)
        
        data = {
            'name':'Jame Son Thomas',
            'username': 'jimmy', 
            'email':'jimmy@awesome.com', 
            'current_password': 'pass',
        }
        
        form = ChangeUserDetailsForm(instance=jack_user, data=data)
        self.assertTrue(form.is_valid())
        form.save()
        
        self.assertTrue(User.objects.filter(username='jimmy').exists(),'User was not registered')
        
        jimmy_user = User.objects.get(username='jimmy')
        
        self.assertEquals(jimmy_user.first_name,'Jame','user First name does not match')
        self.assertEquals(jimmy_user.last_name,'Son Thomas','user Last name does not match')
        self.assertEquals(jimmy_user.email,'jimmy@awesome.com','user Email does not match')        
        self.assertEquals(jimmy_user.username,'jimmy','user username does not match')
        self.assertTrue(jimmy_user.check_password('pass'),'password does not match')
        
        self.assertTrue(jimmy_user.is_active)
        
        data = {
            'name':'Jame Son Thomas',
            'username': 'jimmy', 
            'email':'jame@awesome.com', 
            'current_password': 'wrong-pass',
        }
        
        form = ChangeUserDetailsForm(instance=jimmy_user, data=data)
        self.assertFalse(form.is_valid())    

        data = {
            'name':'Jame Son Thomas',
            'username': '', 
            'email':'jimmy@awesome.com', 
            'current_password': 'pass',
        }
        
        form = ChangeUserDetailsForm(instance=jack_user, data=data)
        self.assertFalse(form.is_valid()) 

        jack_user = create_user_jack(True)
        
        james_user = create_user_james(True)
        
        # check duplicated emails
        data = {
            'name':'James Son Thomas',
            'username': 'james', 
            'email':'jack@awesome.com', 
            'current_password': 'pass',
        }
        
        form = ChangeUserDetailsForm(instance=james_user, data=data)
        self.assertFalse(form.is_valid())
        
        # check duplicated username
        data = {
            'name':'James Son Thomas',
            'username': 'jack', 
            'email':'jack@awesome.com', 
            'current_password': 'pass',
        }
        
        form = ChangeUserDetailsForm(instance=james_user, data=data)
        self.assertFalse(form.is_valid())

    def test_change_password(self):
    
        new_user = create_user_jack(True)
        
        form = ChangeUserPasswordForm(instance=new_user, data={
            'current_password':'pass',
            'new_password':'new_pass',
            'confirm_new_password':'new_pass'
        })
        
        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(new_user.check_password('new_pass'))
        
        form = ChangeUserPasswordForm(instance=new_user, data={
            'current_password':'pass',
            'new_password':'new_pass',
            'confirm_new_password':'no-match'
        })
        
        self.assertFalse(form.is_valid())

        form = ChangeUserPasswordForm(instance=new_user, data={
            'current_password':'pass',
            'new_password':'pass',
            'confirm_new_password':'pass'
        })
        
        self.assertFalse(form.is_valid())
      
        form = ChangeUserPasswordForm(instance=new_user, data={
            'current_password':'pass',
            'new_password':'',
            'confirm_new_password':''
        })
        
        self.assertFalse(form.is_valid())
        
    def test_register(self):
        
        data = {
            'name':'Jack Awesome Daniels',
            'username': 'jack', 
            'email':'jack@awesome.com', 
            'password': 'password',
            'confirm_password':'password'
        }
        
        form = RegisterForm(data=data)
        self.assertTrue(form.is_valid())
        form.save()
        
        self.assertTrue(User.objects.filter(username='jack').exists(),'User was not registered')
        
        new_user = User.objects.get(username='jack')
        
        self.assertEquals(new_user.first_name,'Jack','user First name does not match')
        self.assertEquals(new_user.last_name,'Awesome Daniels','user Last name does not match')
        self.assertEquals(new_user.email,'jack@awesome.com','user Email does not match')        
        self.assertEquals(new_user.username,'jack','user username does not match')
        self.assertTrue(new_user.check_password('password'),'password does not match')
        
        self.assertFalse(new_user.is_active)

        # duplicated username
        data = {
            'name':'Jack',
            'username': 'jack', 
            'email':'jack2@awesome.com', 
            'password': 'password',
            'confirm_password':'password'
        }
        
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())
        
        # duplicated email
        data = {
            'name':'Jack',
            'username': 'jack2', 
            'email':'jack@awesome.com', 
            'password': 'password',
            'confirm_password':'password'
        }
        
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())
        
        # not matching password
        data = {
            'name':'Jack Awesome Daniels',
            'username': 'jack2', 
            'email':'jack2@awesome.com', 
            'password': 'password2',
            'confirm_password':'password'
        }
        
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())