from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.businesses.models import Business


User = get_user_model()


class BusinessModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="owner@example.com",
            password="StrongPassword123!",
        )

    def test_business_belongs_to_owner(self):
        business = Business.objects.create(
            owner=self.user,
            name="Basit Glass Works",
        )

        self.assertEqual(business.owner, self.user)
        self.assertIn(business, self.user.businesses.all())

    def test_user_can_own_multiple_businesses(self):
        Business.objects.create(
            owner=self.user,
            name="Basit Glass Works",
        )
        Business.objects.create(
            owner=self.user,
            name="Amuzara AI",
        )

        self.assertEqual(self.user.businesses.count(), 2)

    def test_business_defaults_to_ghana_and_ghana_cedi(self):
        business = Business.objects.create(
            owner=self.user,
            name="Basit Glass Works",
        )

        self.assertEqual(business.country_code, "GH")
        self.assertEqual(business.currency, "GHS")

    def test_same_business_name_can_exist_for_different_users(self):
        other_user = User.objects.create_user(
            email="other@example.com",
            password="StrongPassword123!",
        )

        Business.objects.create(
            owner=self.user,
            name="Example Business",
        )

        second_business = Business.objects.create(
            owner=other_user,
            name="Example Business",
        )

        self.assertEqual(second_business.name, "Example Business")
        self.assertNotEqual(second_business.owner, self.user)

    def test_business_country_and_currency_can_override_defaults(self):
        business = Business.objects.create(
            owner=self.user,
            name="Canada Consulting Inc",
            country_code="CA",
            currency="CAD",
        )

        self.assertEqual(business.country_code, "CA")
        self.assertEqual(business.currency, "CAD")
