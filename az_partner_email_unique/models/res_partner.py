# Copyright 2022 Andrii Zemlianyi
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import config


class ResPartner(models.Model):
    _inherit = "res.partner"

    email = fields.Char(copy=False)
    same_email_partner_id = fields.Many2one('res.partner',
                                            string='Partner with same email',
                                            compute='_compute_same_email',
                                            store=False)

    @api.constrains("email")
    def _check_email_unique(self):
        for record in self:
            if record.parent_id or not record.email:
                continue
            test_condition = config["test_enable"] \
                and not self.env.context.get(
                "test_email"
            )
            if test_condition:
                continue
            if record.same_email_partner_id:
                raise ValidationError(
                    _("The e-mail %s already exists in another partner.")
                    % record.email
                )

    @api.depends('email', 'company_id')
    def _compute_same_email(self):
        for partner in self:
            # use _origin to deal with onchange()
            partner_id = partner._origin.id
            # active_test = False because if a partner has been deactivated
            # you still want to raise the error, so that you can reactivate
            # it instead of creating a new one, which would loose its history.
            Partner = self.with_context(active_test=False).sudo()
            domain = [
                ('email', '=', partner.email),
                ('company_id', 'in', [False, partner.company_id.id]),
            ]
            if partner_id:
                domain += [('id', '!=', partner_id), '!',
                           ('id', 'child_of', partner_id)]
            partner.same_email_partner_id = bool(
                partner.email) and not partner.parent_id \
                and Partner.search(domain, limit=1)
