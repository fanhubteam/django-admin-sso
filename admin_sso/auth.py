from django.contrib.auth import get_user_model
from admin_sso.models import Assignment

class DjangoSSOAuthBackend:

    def _get_username(self, sso_email):
        '''Method to normalize info that gets assigned to field configured
        under USERNAME_FIELD property of `auth.User` or custom user model.

        Method takes email as input from SSO service and returns username
        before `@domain.com`.

        This method can be overwritten in another backend that inherits
        from `DjangoSSOAuthBackend` if behavior needs to be adjusted.
        '''
        return sso_email.split('@')[0]

    def _get_user(self, sso_email):
        cls = get_user_model()
        try:
            user = cls.objects.get(**{
                cls.USERNAME_FIELD: self._get_username(sso_email)
            })
            # Only return user if email is indeed the same for the account.
            if hasattr(user, 'email') and user.email != sso_email:
                raise ValueError(u'User with same username exists, but email '
                                 'info does\'t match: %s' % user)
            return user
        except cls.DoesNotExist:
            return None

    def _create_user(self, sso_email, is_superuser):
        cls = get_user_model()
        kwargs = {
            cls.USERNAME_FIELD: self._get_username(sso_email),
            'email': sso_email,
            'is_staff': True,
            'is_superuser': is_superuser
        }
        return cls.objects.create(**kwargs)

    def _add_groups(self, user, assignment):
        for group in assignment.groups.all():
            user.groups.add(group)

    def get_user(self, user_id):
        cls = get_user_model()
        try:
            return cls.objects.get(pk=user_id)
        except cls.DoesNotExist:
            return None

    def authenticate(self, request, **kwargs):
        sso_email = kwargs.pop('sso_email', None)

        assignment = Assignment.objects.for_email(sso_email)
        if assignment is None:
            return None

        elif not assignment.user:
            user = self._get_user(sso_email)
            if not user:
                if assignment.create_user:
                    user = self._create_user(sso_email,
                                             assignment.make_superuser)
                    self._add_groups(user, assignment)
                else:
                    return None
            return user

        return assignment.user
