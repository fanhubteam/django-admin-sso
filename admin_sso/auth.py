from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, Group

from admin_sso.models import Assignment


class DjangoSSOAuthBackend(object):
    def get_user(self, user_id):
        cls = get_user_model()
        try:
            return cls.objects.get(pk=user_id)
        except cls.DoesNotExist:
            return None

    def authenticate(self, **kwargs):
        sso_email = kwargs.pop('sso_email', None)

        assignment = Assignment.objects.for_email(sso_email)
        if assignment is None:
            return None

        elif not assignment.user:
            username = sso_email.split('@')[0]
            try:
                # Double check that email is indeed not associated to a user
                user = User.objects.get(email=sso_email)
            except User.DoesNotExist:
                if assignment.create_user:
                    # TODO: This may fail if username is already taken
                    user = User(username=username, email=sso_email)
                    user.is_staff = True
                    user.is_superuser = assignment.make_superuser
                    user.save()
                    for group in assignment.groups.all():
                        user.groups.add(group)
                else:
                    return None
            return user

        return assignment.user
