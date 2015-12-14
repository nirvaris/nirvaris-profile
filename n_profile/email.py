import pdb
import logging
from datetime import date

from django.conf import settings
from django.core.mail.message import EmailMessage
from django.template.loader import render_to_string

from .crypto import user_activation_token

def send_new_password(request, user, new_password):
    
    dic_for_context = {}
    dic_for_context['user'] = user
    dic_for_context['new_password'] = new_password
    dic_for_context['site_url'] = settings.NV_SITE_URL

    subject = render_to_string('forgot-password-email-subject.txt', dic_for_context)
    template = render_to_string('forgot-password-email-body.html', dic_for_context)

    msg = EmailMessage(subject, template, settings.NV_EMAIL_FROM, [user.email])

    msg.content_subtype = "html"  
    msg.send()
    
def send_activation_email(request, user):
    
    #pdb.set_trace()
    
    dic_for_context = {}
    dic_for_context['user'] = user
    dic_for_context['activation_token'] = user_activation_token(user.username, user.email, date.today())
    dic_for_context['site_url'] = settings.NV_SITE_URL

    subject = render_to_string('activation-email-subject.txt', dic_for_context)
    template = render_to_string('activation-email-body.html', dic_for_context)

    msg = EmailMessage(subject, template, settings.NV_EMAIL_FROM, [user.email])

    msg.content_subtype = "html"  
    msg.send()

