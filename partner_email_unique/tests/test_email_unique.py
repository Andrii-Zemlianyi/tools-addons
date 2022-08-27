# Copyright 2022 Andrii Zemlianyi
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestEmailUnique(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestEmailUnique, cls).setUpClass()
        cls.partner_model = cls.env["res.partner"]
        cls.partner = cls.partner_model.create(
            {"name": "Test partner", "email": "test@test.com"}
        )

    def test_duplicated_email_creation(self):
        with self.assertRaises(ValidationError):
            self.partner_model.with_context(test_email=True).create(
                {"name": "Second partner", "email": "test@test.com"}
            )

    def test_duplicate_partner(self):
        partner_copied = self.partner.copy()
        self.assertFalse(partner_copied.email)
