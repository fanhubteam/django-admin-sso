from django import forms

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from admin_sso import settings
from admin_sso.models import Assignment


class AssignmentForm(forms.ModelForm):

    class Meta:
        model = Assignment
        exclude = []

    def clean(self):
        cleaned_data = super(AssignmentForm, self).clean()
        username_mode = cleaned_data.get('username_mode')
        username = cleaned_data.get('username')
        user = cleaned_data.get('user')
        create_user = cleaned_data.get('create_user')
        make_superuser = cleaned_data.get('make_superuser')
        groups = cleaned_data.get('groups')

        ANY = settings.ASSIGNMENT_ANY
        if username_mode is not None and username_mode != ANY and not username:
            self.add_error('username', _("This field is required."))

        if username_mode is not None and username_mode == ANY and username:
            msg = _("This field should be kept empty due to choice selected "
                    "in `Username mode`.")
            self.add_error('username', msg)

        if user and create_user:
            msg = _("Create user option can only be used if the `User` field "
                    "is not set.")
            self.add_error('create_user', msg)

        if not user and not create_user:
            msg = _("A `User` must be chosen or `Create user` flag to be set.")
            raise ValidationError(msg)

        if make_superuser and not create_user:
            msg = _("Make superuser can only be set if `Create user` option "
                    "is enabled.")
            self.add_error('make_superuser', msg)

        if groups and not create_user:
            msg = _("Groups can only be selected if `Create user` option is "
                    "enabled.")
            self.add_error('groups', msg)

        return cleaned_data
