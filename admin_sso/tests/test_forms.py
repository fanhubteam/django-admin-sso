from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase

from admin_sso import settings
from admin_sso.forms import AssignmentForm
#from admin_sso.models import Assignment


User = get_user_model()


class AuthModuleTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='admin_sso1')
        self.data = dict(
            username='',
            username_mode=settings.ASSIGNMENT_ANY,
            domain='example.com',
            user=self.user.id,
            weight=100
        )

    def tearDown(self):
        self.user.delete()

    def test_empty_form(self):
        form = AssignmentForm(data={})
        self.assertFalse(form.is_valid())

    def test_assignment_any_expected_data(self):
        form = AssignmentForm(data=self.data)
        self.assertTrue(form.is_valid())

    def test_assignment_any_with_unexpected_username(self):
        self.data.update({'username': 'foo'})
        form = AssignmentForm(data=self.data)
        self.assertEqual(
            form.errors['username'],
            [u"This field should be kept empty due to choice selected in "
                "`Username mode`."]
        )

    def test_assignment_match_without_username(self):
        self.data.update({'username_mode': settings.ASSIGNMENT_MATCH})
        form = AssignmentForm(data=self.data)
        self.assertEqual(
            form.errors['username'],
            [u"This field is required."]
        )

    def test_assignment_except_without_username(self):
        self.data.update({'username_mode': settings.ASSIGNMENT_EXCEPT})
        form = AssignmentForm(data=self.data)
        self.assertEqual(
            form.errors['username'],
            [u"This field is required."]
        )

    def test_assignment_without_expected_user_or_create_user_flag(self):
        self.data.update({'user': None})
        form = AssignmentForm(data=self.data)
        self.assertEqual(
            form.errors['__all__'],
            [u"A `User` must be chosen or `Create user` flag to be set."]
        )

    def test_assignment_with_user_and_create_user_flag(self):
        self.data.update({'create_user': True})
        form = AssignmentForm(data=self.data)
        self.assertEqual(
            form.errors['create_user'],
            [u"Create user option can only be used if the `User` field is "
                "not set."]
        )

    def test_assignment_with_make_superuser_without_create_user_flag(self):
        self.data.update({'make_superuser': True})
        form = AssignmentForm(data=self.data)
        self.assertEqual(
            form.errors['make_superuser'],
            [u"Make superuser can only be set if `Create user` option "
                "is enabled."]
        )

    def test_assignment_with_groups_without_create_user_flag(self):
        group = Group.objects.create(name='stuff')
        self.data.update({'groups': [group.id]})
        form = AssignmentForm(data=self.data)
        self.assertEqual(
            form.errors['groups'],
            [u"Groups can only be selected if `Create user` option is "
                "enabled."]
        )
