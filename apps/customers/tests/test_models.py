from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.customers.models import Customer


User = get_user_model()


class CustomerModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="owner@example.com",
            password="StrongPassword123!",
        )

    def test_customer_belongs_to_owner(self):
        customer = Customer.objects.create(
            owner=self.user,
            name="Kwame Mensah",
        )

        self.assertEqual(customer.owner, self.user)
        self.assertIn(customer, self.user.customers.all())

    def test_user_can_own_multiple_customers(self):
        Customer.objects.create(
            owner=self.user,
            name="Kwame Mensah",
        )
        Customer.objects.create(
            owner=self.user,
            name="Ama Boateng",
        )

        self.assertEqual(self.user.customers.count(), 2)

    def test_same_customer_name_can_exist_for_different_users(self):
        other_user = User.objects.create_user(
            email="other@example.com",
            password="StrongPassword123!",
        )

        Customer.objects.create(
            owner=self.user,
            name="Kwame Mensah",
        )

        second_customer = Customer.objects.create(
            owner=other_user,
            name="Kwame Mensah",
        )

        self.assertEqual(second_customer.name, "Kwame Mensah")
        self.assertNotEqual(second_customer.owner, self.user)

    def test_customer_phone_and_email_are_not_globally_unique(self):
        Customer.objects.create(
            owner=self.user,
            name="Kwame Mensah",
            phone="+233201234567",
            email="shared@example.com",
        )

        second_customer = Customer.objects.create(
            owner=self.user,
            name="Kwame Mensah Junior",
            phone="+233201234567",
            email="shared@example.com",
        )

        self.assertEqual(second_customer.phone, "+233201234567")
        self.assertEqual(second_customer.email, "shared@example.com")
