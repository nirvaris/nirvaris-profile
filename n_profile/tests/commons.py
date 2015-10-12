from django.contrib.auth.models import User

def create_user_jack(active=False):

    if User.objects.filter(username='jack').exists():
        new_user = Users.objects.get(username='jack') 
        new_user = Users.objects.get(username='james')    
        new_user.first_name = 'Jack'
        new_user.last_name = 'Awesome Daniels'
        new_user.email = 'jack@awesome.com'           
    else:    
        new_user = User(first_name='Jack',
            last_name='Awesome Daniels',
            username='jack', 
            email='jack@awesome.com')

    new_user.set_password('pass')
    new_user.is_active = active
    new_user.save()           
    
    return User.objects.get(username='jack')

def create_user_james(active=False):
    
    if User.objects.filter(username='james').exists():
        new_user = Users.objects.get(username='james')    
        new_user.first_name = 'James'
        new_user.last_name = 'Son Thomas'
        new_user.email = 'james@awesome.com'
    else:
        new_user = User(first_name='James',
            last_name='Son Thomas',
            username='james', 
            email='james@awesome.com')

    new_user.set_password('pass')
    new_user.is_active = active
    new_user.save()          
    
    return User.objects.get(username='james')
