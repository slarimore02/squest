import base64

from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import get_template

from service_catalog import tasks
from service_catalog.models.request import RequestState

DEFAULT_FROM_EMAIL = f"squest@{settings.SQUEST_EMAIL_HOST}"
EMAIL_TITLE_PREFIX = "[Squest]"


def _add_user_in_user_list(user, user_list):
    if user.email and user.profile.notification_enabled and user.email not in user_list:
        user_list.append(user.email)
    return user_list


def _remove_user_in_user_list(user, user_list):
    if user.profile.notification_enabled and user.email and user.email in user_list:
        user_list.remove(user.email)
    return user_list


def _get_subject(target_object):
    return f"{EMAIL_TITLE_PREFIX} {target_object.__class__.__name__} #{target_object.id} - {target_object}"


def _get_headers(subject):
    email_id = str(base64.b64encode(subject.encode()))
    headers = dict()
    headers["Message-ID"] = email_id
    headers["In-Reply-To"] = email_id
    headers["References"] = email_id
    return headers


def _get_admin_emails(instance=None, request=None):
    """
    Return a list of admin (is_staff) email if notification is enabled and target service subscribed
    :return:
    """
    admins = User.objects.filter(is_staff=True)
    # create a list of email
    email_admins = list()
    for admin in admins:
        if admin.email and admin.profile.notification_enabled and admin.profile.is_notification_authorized(instance, request):
            email_admins.append(admin.email)
    return email_admins


def _get_receivers_for_request_message(request_message):
    receiver_email_list = _get_admin_emails(instance=request_message.request.instance, request=request_message.request)
    receiver_email_list = _add_user_in_user_list(request_message.request.user, receiver_email_list)
    receiver_email_list = _remove_user_in_user_list(request_message.sender, receiver_email_list)
    return receiver_email_list


def _get_receivers_for_support_message(support_message):
    receiver_email_list = _get_admin_emails(instance=support_message.support.instance)
    receiver_email_list = _add_user_in_user_list(support_message.support.instance.spoc, receiver_email_list)
    receiver_email_list = _remove_user_in_user_list(support_message.sender, receiver_email_list)
    return receiver_email_list


def send_mail_request_update(target_request, user_applied_state=None, message=None, receiver_email_list=None,
                             plain_text=None):
    """
    Notify users that a request has been updated
    :param message: A message to add to the email
    :param user_applied_state: string email of the user who send the notification
    :type user_applied_state: User
    :param target_request:
    :type target_request: service_catalog.models.request.Request
    :param receiver_email_list: email diffusion list
    :type receiver_email_list: List
    :param plain_text: text displayed in the mail
    :type plain_text: String
    :return:
    """
    if not settings.SQUEST_EMAIL_NOTIFICATION_ENABLED:
        return

    subject = _get_subject(target_request)
    template_name = "service_catalog/mails/request_state_update.html"

    context = {'request': target_request,
               'user_applied_state': user_applied_state,
               'current_site': settings.SQUEST_HOST,
               'message': message}
    if plain_text is None:
        plain_text = f"Request state update: {target_request.state}"
        if target_request.state == RequestState.SUBMITTED:
            plain_text = f"Request update for service: {target_request.instance.name}"
    html_template = get_template(template_name)
    html_content = html_template.render(context)
    if target_request.approval_step:
        receiver_email_list = target_request.approval_step.get_approvers_emails()
    if receiver_email_list is None:
        receiver_email_list = _get_admin_emails(instance=target_request.instance, request=target_request)  # email sent to all admins
    if target_request.user.profile.notification_enabled and target_request.user.email:
        receiver_email_list.append(target_request.user.email)  # email sent to the requester
    tasks.send_email.delay(subject, plain_text, html_content, DEFAULT_FROM_EMAIL,
                           bcc=receiver_email_list,
                           headers=_get_headers(subject))


def send_mail_new_support_message(message):
    if not settings.SQUEST_EMAIL_NOTIFICATION_ENABLED:
        return
    subject = _get_subject(message.support)
    template_name = "service_catalog/mails/support.html"
    plain_text = f"New support message received on Instance #{message.support.instance.id} (#{message.support.id})"
    context = {'message': message, 'current_site': settings.SQUEST_HOST}
    html_template = get_template(template_name)
    html_content = html_template.render(context)
    receiver_email_list = _get_receivers_for_support_message(message)
    tasks.send_email.delay(subject, plain_text, html_content, DEFAULT_FROM_EMAIL,
                           bcc=receiver_email_list,
                           headers=_get_headers(subject))


def send_mail_support_is_closed(support):
    if not settings.SQUEST_EMAIL_NOTIFICATION_ENABLED:
        return
    subject = _get_subject(support)
    template_name = "service_catalog/mails/closed_support.html"
    plain_text = f"Support closed on Instance #{support.instance.id} (#{support.id})"
    context = {'support': support, 'current_site': settings.SQUEST_HOST}
    html_template = get_template(template_name)
    html_content = html_template.render(context)
    receiver_email_list = [intervenant.email for intervenant in support.get_all_intervenants()]
    tasks.send_email.delay(subject, plain_text, html_content, DEFAULT_FROM_EMAIL,
                           bcc=receiver_email_list,
                           headers=_get_headers(subject))


def send_mail_new_comment_on_request(message):
    if not settings.SQUEST_EMAIL_NOTIFICATION_ENABLED:
        return
    subject = _get_subject(message.request)
    template_name = "service_catalog/mails/comment.html"
    plain_text = f"New comment received on Request #{message.request.id}"
    context = {'message': message, 'current_site': settings.SQUEST_HOST}
    html_template = get_template(template_name)
    html_content = html_template.render(context)
    receiver_email_list = _get_receivers_for_request_message(message)
    tasks.send_email.delay(subject, plain_text, html_content, DEFAULT_FROM_EMAIL,
                           bcc=receiver_email_list,
                           headers=_get_headers(subject))


def send_email_request_canceled(target_request, user_applied_state=None, request_owner_user=None):
    """
    :param target_request: Request model
    :type target_request: service_catalog.models.request.Request
    :param user_applied_state: user who called this method
    :type user_applied_state: User
    :param request_owner_user: user owner of the Request
    :type request_owner_user: User
    :return:
    """
    if not settings.SQUEST_EMAIL_NOTIFICATION_ENABLED:
        return
    subject = _get_subject(target_request)
    plain_text = f"Request #{target_request.id} - CANCELLED"
    template_name = "service_catalog/mails/request_cancelled.html"
    context = {'request_id': target_request.id,
               'user_applied_state': user_applied_state,
               'current_site': settings.SQUEST_HOST}
    html_template = get_template(template_name)
    html_content = html_template.render(context)
    receiver_email_list = _get_admin_emails(request=target_request)  # email sent to all admins
    if request_owner_user.profile.notification_enabled and request_owner_user.email:
        receiver_email_list.append(request_owner_user.email)  # email sent to the requester
    tasks.send_email.delay(subject, plain_text, html_content, DEFAULT_FROM_EMAIL,
                           bcc=receiver_email_list,
                           headers=_get_headers(subject))
