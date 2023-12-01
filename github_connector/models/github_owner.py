from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class GithubOwner(models.Model):
    _name = "github.owner"
    _inherit = "abstract.github.model"
    _order = "name"
    _description = "Github Owner"
    _github_login_field = "login"

    _TYPE_SELECTION = [
        ("organization", "Organization"),
        ("user", "User"),
    ]

    name = fields.Char(string="Owner Name")

    type = fields.Selection(
        selection=_TYPE_SELECTION,
        required=True,
    )

    organisation_id = fields.Many2one(
        comodel_name="github.organisation", string="Organisation"
    )

    github_user_id = fields.Many2one(comodel_name="res.partner", string="User")

    @api.model
    def get_conversion_dict(self):
        res = super(GithubOwner, self).get_conversion_dict()
        res.update(
            {
                "type": "type",
            }
        )
        return res

    @api.constrains("type", "organisation_id", "user_id")
    def _check_type_organisation(self):
        owner_type_field_map = {
            "user": "user_id",
            "organisation": "organisation_id",
        }
        for owner in self.filtered(
            lambda o: not o.organisation_id or not o.github_user_id
        ):
            raise ValidationError(
                _(
                    "field %(fname)s is required for owner of type %(owner_type)s",
                    **dict(
                        fname=self._fields[owner_type_field_map[owner.type]].string
                        or owner_type_field_map[owner.type],
                        owner_type=owner.type,
                    )
                )
            )
