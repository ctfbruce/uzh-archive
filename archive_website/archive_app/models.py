# models.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.conf import settings
from .managers import DocumentManager, UserManager
from datetime import timedelta
from django.utils import timezone
from .utils import send_verification_email

class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    is_moderator = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
    
    def has_perm(self, perm, obj=None):
        return True  # Customize this if you need specific permission handling

    def has_module_perms(self, app_label):
        return True  # Customize this if you need specific app-level permission handling

    
    
    @property
    def is_staff(self):
        return self.is_admin


class Verification_Code(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False, on_delete=models.CASCADE,related_name='verification_code')
    expires_by = models.DateTimeField(default=timezone.now() + timedelta(minutes=5))
    code = models.CharField(max_length=20)

    def is_valid(self):
        return timezone.now() < self.expires_by

    def __str__(self):
        return f'{self.user.email} - {self.code}'
    
    

class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=100)
    tags = models.ManyToManyField(Tag, related_name='subjects')

    def __str__(self):
        return self.name

def user_directory_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/subject-year-semester-type-language.pdf
    return f"{instance.subject.name}-{instance.year}-{instance.semester}-{instance.type}-{instance.language}.pdf"

DOCUMENT_TYPE_CHOICES = [
    ('past_exam', 'Past Exam'),
    ('exam_solution', 'Past Exam Solution'),
    ('summary', 'Summary'),
    ('question_bank', 'Question Bank'),
    ('other', 'Other'),
]

SEMESTER_CHOICES = [
    ('HS', 'HS'),
    ('FS', 'FS'),
]

YEAR_CHOICES = [(year, str(year)) for year in range(2015, 2025)]

class Document(models.Model):
    type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    semester = models.CharField(max_length=2, choices=SEMESTER_CHOICES)
    year = models.PositiveIntegerField(choices=YEAR_CHOICES)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='uploaded_documents',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    uploaded_by_email = models.EmailField(null=True, blank=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='verified_documents',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    verified_by_email = models.EmailField(null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, related_name='documents', null=True)
    file = models.FileField(upload_to=user_directory_path)
    upvotes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='upvoted_documents', blank=True)
    description = models.TextField(blank=True, null=True)
    language = models.CharField(max_length=10, default='EN')

    objects = DocumentManager()

    def __str__(self):
        return f"{self.subject.name} - {self.year} {self.semester} - {self.get_type_display()}"

    @property
    def upvote_count(self):
        return self.upvotes.count()

# Signal to handle user deletion
@receiver(pre_delete, sender=User)
def replace_user_with_email(sender, instance, **kwargs):
    email_placeholder = instance.email
    Document.objects.filter(uploaded_by=instance).update(
        uploaded_by=None, uploaded_by_email=email_placeholder
    )
    Document.objects.filter(verified_by=instance).update(
        verified_by=None, verified_by_email=email_placeholder
    )
