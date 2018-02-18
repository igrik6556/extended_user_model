# -*- coding: utf-8 -*-
import hashlib
import random
import datetime
from extended_user import settings
from django.db import models
from django.urls import reverse
from django.utils import six, timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.validators import ASCIIUsernameValidator, UnicodeUsernameValidator
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.template.loader import render_to_string

from django.utils.translation import ugettext as _

EMAIL_CONFIRMATION_DAYS = getattr(settings, "EMAIL_CONFIRMATION_DAYS", 1)

GENDER_USER = (
    ('NS', _('Not specified')),
    ('ML', _('Male')),
    ('FM', _('Female'))
)


class UserManager(BaseUserManager):
    def _create_user(self, username, email, password, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_confirm', True)
        return self._create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        db_table = 'User'
        verbose_name = _('user')
        verbose_name_plural = _('users')

    username_validator = UnicodeUsernameValidator() if six.PY3 else ASCIIUsernameValidator()

    username = models.CharField(
        _('Username'),
        max_length=100,
        unique=True,
        help_text=_('100 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(
        _('First name'),
        max_length=30,
        blank=True,
        null=True,
    )
    last_name = models.CharField(
        _('Last name'),
        max_length=50,
        blank=True,
        null=True,
    )
    email = models.EmailField(
        _('Email address'),
        unique=True,
    )
    gender = models.CharField(
        _('Gender'),
        max_length=2,
        choices=GENDER_USER,
        blank=True,
        default='NS',
    )
    birthday = models.DateField(
        _('Date of birth'),
        blank=True,
        null=True,
    )
    avatar = models.ImageField(
        _('User avatar'),
        upload_to='user_avatars',
        blank=True,
        null=True,
    )
    date_joined = models.DateTimeField(
        _('date joined'),
        default=timezone.now,
    )
    is_confirm = models.BooleanField(
        _('Confirm'),
        default=False,
        help_text=_('Designates whether the user can log in.'),
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=False,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def get_full_name(self):
        full_name = '{0} {1}'.format(self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.username

    def __str__(self):
        return '{0} ({1})'.format(self.username, self.email)

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)
        if not self.is_active:
            EmailConfirmation.objects.send_confirm_email(self)


class EmailConfirmationManager(models.Manager):
    def send_confirm_email(self, user):
        confirmation_key = hashlib.sha256((str(random.random())+user.email).encode('utf-8')).hexdigest()[:40]
        try:
            curr_site = Site.objects.get_current()
        except Site.DoesNotExist:
            return

        subject = _("Confirmation of registration at the %(site)s") % {'site': curr_site.name}
        path = reverse('extuser:confirmation', kwargs={'key': confirmation_key})
        activate_url = 'http://{0}{1}'.format(curr_site.domain, path)
        ctx = {
            'site': curr_site,
            'user': user,
            'activate_url': activate_url,
        }
        message = render_to_string('extuser/confirmation_email.html', ctx)

        send_mail(subject, '', settings.EMAIL_HOST_USER, [user.email, ], html_message=message)

        return self.create(
            user=user,
            confirmation_key=confirmation_key,
            sent=timezone.now()
        )

    def confirmation(self, key):
        try:
            confirmation = self.get(confirmation_key=key)
        except self.model.DoesNotExist:
            return None
        user = confirmation.user
        if not confirmation.expire_dt():
            user.is_confirm = True
            user.is_active = True
            user.save()
        return user


class EmailConfirmation(models.Model):
    class Meta:
        verbose_name = _('Email confirmation')

    user = models.OneToOneField(
        User,
        verbose_name=_('User'),
    )
    confirmation_key = models.CharField(
        _('Confirmation key'),
        max_length=40,
    )
    sent = models.DateTimeField()

    objects = EmailConfirmationManager()

    def __str__(self):
        return 'Confirmation for {0}'.format(self.user)

    def expire_dt(self):
        expired = self.sent + datetime.timedelta(days=EMAIL_CONFIRMATION_DAYS)
        return timezone.now() >= expired
