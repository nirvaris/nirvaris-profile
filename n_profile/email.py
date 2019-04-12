from datetime import date

from django.conf import settings
from django.core.mail.message import EmailMessage
# from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .crypto import user_activation_token, user_invitation_token


def get_invitation_infos(request, email, groups):
    dic_for_context = {'user': request.user,
                       'invitation_token': user_invitation_token(email, date.today(), groups),
                       'site_url': settings.NV_SITE_URL}
    return dic_for_context


def send_invitation_email(request, email, groups):
    # pdb.set_trace()

    dic_for_context = get_invitation_infos(request, email, groups)

    subject = render_to_string('email-subject-invitation.txt', dic_for_context)
    template = render_to_string('email-body-invitation.html', dic_for_context)

    msg = EmailMessage(subject, template, settings.NV_EMAIL_FROM, [email])
    # msg = EmailMultiAlternatives(subject, template, settings.NV_EMAIL_FROM, [email])

    msg.content_subtype = "html"
    msg.send()
    return dic_for_context


def send_new_password(request, user, new_password):
    dic_for_context = {}
    dic_for_context['user'] = user
    dic_for_context['new_password'] = new_password
    dic_for_context['site_url'] = settings.NV_SITE_URL

    subject = render_to_string('email-subject-forgot-password.txt', dic_for_context)
    template = render_to_string('email-body-forgot-password.html', dic_for_context)

    msg = EmailMessage(subject, template, settings.NV_EMAIL_FROM, [user.email])
    # msg = EmailMultiAlternatives(subject, template, settings.NV_EMAIL_FROM, [user.email])
    msg.content_subtype = "html"
    msg.send()


def send_activation_email(request, user):
    # pdb.set_trace()

    dic_for_context = {}
    dic_for_context['user'] = user
    dic_for_context['activation_token'] = user_activation_token(user.username, user.email, date.today())
    dic_for_context['site_url'] = settings.NV_SITE_URL

    subject = render_to_string('email-subject-activation.txt', dic_for_context)
    template = render_to_string('email-body-activation.html', dic_for_context)

    msg = EmailMessage(subject, template, settings.NV_EMAIL_FROM, [user.email])

    msg.content_subtype = "html"
    msg.send()
