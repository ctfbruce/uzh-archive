import random
import string
from django.core.mail import send_mail
from django.conf import settings

def generate_verification_code(length=20):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def send_verification_email(user_email, verification_code):

    subject = 'UZH Learning Resources - Email Verification'
    message = f"""Your verification code is: {verification_code}"""
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user_email]
    
    send_mail(subject, message, email_from, recipient_list)


