# -*- coding: utf-8 -*-
from django.db import models
from django.utils import six, timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.contrib.auth.validators import ASCIIUsernameValidator, UnicodeUsernameValidator

from django.utils.translation import ugettext as _


GENDER_USER = (
    ('NS', _('Not specified')),
    ('ML', _('Male')),
    ('FM', _('Female'))
)


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
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.username

    def __str__(self):
        return '%s (%s)' % (self.username, self.email)
