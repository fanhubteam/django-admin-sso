from __future__ import unicode_literals

import fnmatch

from django.contrib.auth.models import Group
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from admin_sso import settings


class AssignmentManager(models.Manager):
    def for_email(self, email):
        if not email:
            return None

        try:
            username, domain = email.split('@')
        except ValueError:
            return None
        possible_assignments = self.filter(domain=domain)
        used_assignment = None
        for assignment in possible_assignments:
            if assignment.username_mode == settings.ASSIGNMENT_ANY:
                used_assignment = assignment
                break
            elif assignment.username_mode == settings.ASSIGNMENT_MATCH:
                if fnmatch.fnmatch(username, assignment.username):
                    used_assignment = assignment
                    break
            elif assignment.username_mode == settings.ASSIGNMENT_EXCEPT:
                if not fnmatch.fnmatch(username, assignment.username):
                    used_assignment = assignment
                    break
        if used_assignment is None:
            return None
        return used_assignment


@python_2_unicode_compatible
class Assignment(models.Model):
    username_mode = models.IntegerField(
        choices=settings.ASSIGNMENT_CHOICES,
        help_text=_(
            'Defines which mode/rule will be used to allow accounts '
            'to login.')
    )
    username = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Example: john')
    )
    domain = models.CharField(
        max_length=255,
        help_text=_('A domain with Oauth support. Example: mywebsite.com')
    )
    copy = models.BooleanField(default=False)
    weight = models.PositiveIntegerField(
        default=0,
        help_text=_(
            'Specifies the order in which this assignment will be taken into '
            'account compared to others. Bigger weights are processed first.'
        )
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text=_(
            'User to be used on login for this assignment. Useful '
            'when using a different remote username.'
        )
    )
    create_user = models.BooleanField(
        default=False,
        help_text=_(
            'Create a user upon first login for every account. '
            'Subsequent logins are done matching account\'s email address.'
        )
    )
    make_superuser = models.BooleanField(
        default=False,
        help_text=_('Whether the created user(s) should be superusers or not.')
    )
    groups = models.ManyToManyField(
        Group,
        blank=True,
        help_text=_(
            'List of groups that users should be added to on account creation.'
        )
    )

    class Meta:
        ordering = ('-weight',)
        verbose_name = _('Assignment')
        verbose_name_plural = _('Assignments')

    def __str__(self):
        return "%s (%s) @%s" % (
            dict(settings.ASSIGNMENT_CHOICES)[self.username_mode],
            self.username,
            self.domain,
        )

    objects = AssignmentManager()
