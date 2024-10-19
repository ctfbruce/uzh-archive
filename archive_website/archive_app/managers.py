# managers.py

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.models import BaseUserManager
import re

class DocumentManager(models.Manager):
    def filter_by_criteria(self, subject=None, doc_type=None, year=None, semester=None):
        queryset = self.get_queryset()
        if subject:
            queryset = queryset.filter(subject=subject)
        if doc_type:
            queryset = queryset.filter(type=doc_type)
        if year:
            queryset = queryset.filter(year=year)
        if semester:
            queryset = queryset.filter(semester=semester)
        return queryset

    def approved_documents(self):
        return self.get_queryset().filter(verified_by__isnull=False)

    def pending_documents(self):
        return self.get_queryset().filter(verified_by__isnull=True)

    def upvote_document(self, document, user):
        document.upvotes.add(user)
        document.save()

    def downvote_document(self, document, user):
        document.upvotes.remove(user)
        document.save()






class UserManager(BaseUserManager):
    def create_user(self, email, password=None, is_moderator=False, is_verified=False):
        if not email:
            raise ValueError('Users must have an email address')

        if not self._validate_uzh_email(email):
            raise ValueError('Email must be in the form firstname.lastname@uzh.ch')

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_moderator=is_moderator,
            is_verified=is_verified,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def _validate_uzh_email(self, email):
        pattern = r'^[a-z]+\.[a-z]+@uzh\.ch$'
        return re.match(pattern, email.lower())

    def create_superuser(self, email, password):
        if not email:
            raise ValueError('Superusers must have an email address')

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_moderator=True,
            is_verified=True,
            is_admin=True,
            # is_superuser=True,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
