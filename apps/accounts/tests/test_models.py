from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase


User = get_user_model()


class UserModelTests(TestCase):
    def test_create_user_with_email_and_password(self):
        user = User.objects.create_user(
            email="basit@example.com",
            password="StrongPassword123!",
            first_name="Amuzu",
            last_name="Abdul Basit",
        )

        self.assertEqual(user.email, "basit@example.com")
        self.assertEqual(user.first_name, "Amuzu")
        self.assertEqual(user.last_name, "Abdul Basit")
        self.assertTrue(user.check_password("StrongPassword123!"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_email_domain_is_normalized(self):
        user = User.objects.create_user(
            email="basit@EXAMPLE.COM",
            password="StrongPassword123!",
        )

        self.assertEqual(user.email, "basit@example.com")

    def test_email_is_required(self):
        with self.assertRaisesMessage(
            ValueError,
            "Users must have an email address.",
        ):
            User.objects.create_user(
                email="",
                password="StrongPassword123!",
            )

    def test_password_is_hashed(self):
        raw_password = "StrongPassword123!"

        user = User.objects.create_user(
            email="basit@example.com",
            password=raw_password,
        )

        self.assertNotEqual(user.password, raw_password)
        self.assertTrue(user.check_password(raw_password))

    def test_duplicate_email_is_rejected(self):
        User.objects.create_user(
            email="basit@example.com",
            password="StrongPassword123!",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                User.objects.create_user(
                    email="basit@example.com",
                    password="AnotherPassword123!",
                )

    def test_create_superuser_sets_required_flags(self):
        user = User.objects.create_superuser(
            email="admin@example.com",
            password="StrongPassword123!",
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_superuser_requires_password(self):
        with self.assertRaisesMessage(
            ValueError,
            "Superusers must have a password.",
        ):
            User.objects.create_superuser(
                email="admin@example.com",
                password=None,
            )

    def test_email_is_authentication_identifier(self):
        self.assertEqual(User.USERNAME_FIELD, "email")
        self.assertTrue(User._meta.get_field("email").unique)
