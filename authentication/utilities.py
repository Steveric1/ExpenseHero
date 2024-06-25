from django.contrib.auth.base_user import AbstractBaseUser
from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type


def email_sender(subject, message, recipient_list):
    if isinstance(recipient_list, str):
        recipient_list = [recipient_list]

    send_mail(
        subject,
        message,
        'noreply@expensehero.com',
        recipient_list,
        fail_silently=False,
    )


class TokenGenereator(PasswordResetTokenGenerator):
    """Token Generator"""

    def _make_hash_value(self, user: AbstractBaseUser, timestamp: int) -> str:
        return (text_type(user.is_active) + text_type(user.pk) +
                text_type(timestamp))

token_generator = TokenGenereator()