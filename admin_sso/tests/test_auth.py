from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.contrib.auth.models import Group

from admin_sso import settings
from admin_sso.auth import DjangoSSOAuthBackend
from admin_sso.models import Assignment


User = get_user_model()


class AuthModuleTests(TestCase):
    def setUp(self):
        self.auth_module = DjangoSSOAuthBackend()
        self.user = User.objects.create(username="admin_sso1")
        self.assignment1 = Assignment.objects.create(
            username="",
            username_mode=settings.ASSIGNMENT_ANY,
            domain="example.com",
            user=self.user,
            weight=100,
        )
        self.request_factory = RequestFactory()

    def tearDown(self):
        self.user.delete()
        Assignment.objects.all().delete()

    def test_empty_authenticate(self):
        request = self.request_factory.get("/")
        user = self.auth_module.authenticate(request)
        self.assertEqual(user, None)

    def test_simple_assignment(self):
        email = "foo@example.com"
        request = self.request_factory.get("/")
        user = self.auth_module.authenticate(request, sso_email=email)
        self.assertEqual(user, self.user)

    def test_assignment_without_user(self):
        self.assignment1.user = None
        self.assignment1.save()
        email = "foo@example.com"
        user = self.auth_module.authenticate(sso_email=email)
        self.assertIsNone(user)

    def test_assignment_without_user_create_user(self):
        self.assignment1.create_user = True
        self.assignment1.user = None
        self.assignment1.save()
        email = "foo@example.com"
        user = self.auth_module.authenticate(sso_email=email)
        self.assertEqual(user.username, email.split('@')[0])
        self.assertFalse(user.is_superuser)

    def test_assignment_without_user_create_superuser(self):
        self.assignment1.create_user = True
        self.assignment1.make_superuser = True
        self.assignment1.user = None
        self.assignment1.save()
        email = "foo@example.com"
        user = self.auth_module.authenticate(sso_email=email)
        self.assertEqual(user.username, email.split('@')[0])
        self.assertTrue(user.is_superuser)

    def test_assignment_without_user_create_user_add_groups(self):
        self.assignment1.create_user = True
        self.assignment1.groups.add(
            Group.objects.get_or_create(name='staff')[0]
        )
        self.assignment1.user = None
        self.assignment1.save()
        email = "foo@example.com"
        user = self.auth_module.authenticate(sso_email=email)
        self.assertTrue(user.groups.filter(name='staff').exists())

    def test_get_user(self):
        user = self.auth_module.get_user(self.user.id)
        self.assertEqual(user, self.user)

        user = self.auth_module.get_user(self.user.id + 42)
        self.assertEqual(user, None)


class AssignmentManagerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="admin_sso1")
        self.assignment1 = Assignment.objects.create(
            username="",
            username_mode=settings.ASSIGNMENT_ANY,
            domain="example.com",
            user=self.user,
            weight=100,
        )
        self.assignment2 = Assignment.objects.create(
            username="*bar",
            username_mode=settings.ASSIGNMENT_MATCH,
            domain="example.com",
            user=self.user,
            weight=200,
        )
        self.assignment3 = Assignment.objects.create(
            username="foo*",
            username_mode=settings.ASSIGNMENT_EXCEPT,
            domain="example.com",
            user=self.user,
            weight=300,
        )

    def tearDown(self):
        self.user.delete()
        Assignment.objects.all().delete()

    def test_domain_matches(self):
        email = "foo@example.com"
        user = Assignment.objects.for_email(email)
        self.assertEqual(user, self.assignment1)

    def test_invalid_domain(self):
        email = "someone@someotherdomain.com"
        user = Assignment.objects.for_email(email)
        self.assertIsNone(user)

    def test_domain_matches_and_username_ends_with_bar(self):
        email = "foobar@example.com"
        user = Assignment.objects.for_email(email)
        self.assertEqual(user, self.assignment2)

    def test_domain_matches_and_username_doesnt_begin_with_foo(self):
        email = "bar@example.com"
        user = Assignment.objects.for_email(email)
        self.assertEqual(user, self.assignment3)

    def test_invalid_email(self):
        email = "invalid"
        user = Assignment.objects.for_email(email)
        self.assertEqual(user, None)

    def test_change_weight(self):
        self.assignment2.weight = 50
        self.assignment2.save()
        email = "foobar@example.com"
        user = Assignment.objects.for_email(email)
        self.assertEqual(user, self.assignment1)
