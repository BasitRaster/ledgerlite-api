from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.businesses.models import Business
from apps.customers.models import BusinessCustomer, Customer


User = get_user_model()


class BusinessCustomerModelTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="StrongPassword123!",
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="StrongPassword123!",
        )

        self.business = Business.objects.create(
            owner=self.owner,
            name="Basit Glass Works",
        )

        self.customer = Customer.objects.create(
            owner=self.owner,
            name="Kwame Mensah",
        )

        self.other_customer = Customer.objects.create(
            owner=self.other_user,
            name="Another User Customer",
        )

    def test_business_can_link_to_customer_with_same_owner(self):
        relationship = BusinessCustomer.objects.create(
            business=self.business,
            customer=self.customer,
        )

        self.assertEqual(relationship.business, self.business)
        self.assertEqual(relationship.customer, self.customer)
        self.assertIn(
            relationship,
            self.business.customer_links.all(),
        )
        self.assertIn(
            relationship,
            self.customer.business_links.all(),
        )

    def test_cross_tenant_relationship_is_rejected(self):
        with self.assertRaisesMessage(
            ValidationError,
            "Business and customer must belong to the same user.",
        ):
            BusinessCustomer.objects.create(
                business=self.business,
                customer=self.other_customer,
            )

    def test_same_business_customer_pair_cannot_be_created_twice(self):
        BusinessCustomer.objects.create(
            business=self.business,
            customer=self.customer,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                BusinessCustomer.objects.create(
                    business=self.business,
                    customer=self.customer,
                )

    def test_customer_can_link_to_multiple_businesses_of_same_owner(self):
        second_business = Business.objects.create(
            owner=self.owner,
            name="Amuzara AI",
        )

        BusinessCustomer.objects.create(
            business=self.business,
            customer=self.customer,
        )
        BusinessCustomer.objects.create(
            business=second_business,
            customer=self.customer,
        )

        self.assertEqual(
            self.customer.business_links.count(),
            2,
        )

    def test_deleting_business_removes_relationship_not_customer(self):
        relationship = BusinessCustomer.objects.create(
            business=self.business,
            customer=self.customer,
        )

        customer_id = self.customer.id
        relationship_id = relationship.id

        self.business.delete()

        self.assertFalse(
            BusinessCustomer.objects.filter(
                id=relationship_id,
            ).exists()
        )
        self.assertTrue(
            Customer.objects.filter(
                id=customer_id,
            ).exists()
        )

    def test_deleting_customer_removes_relationship_not_business(self):
        relationship = BusinessCustomer.objects.create(
            business=self.business,
            customer=self.customer,
        )

        business_id = self.business.id
        relationship_id = relationship.id

        self.customer.delete()

        self.assertFalse(
            BusinessCustomer.objects.filter(
                id=relationship_id,
            ).exists()
        )
        self.assertTrue(
            Business.objects.filter(
                id=business_id,
            ).exists()
        )
