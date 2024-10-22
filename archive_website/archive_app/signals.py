from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Verification_Code
from .utils import send_verification_email

@receiver(post_save, sender=Verification_Code)
def send_verification_email_signal(sender, instance, created, **kwargs):
    if created:
        send_verification_email(instance.user.email, instance.code)