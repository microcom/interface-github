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

    organization_id = fields.Many2one(
        comodel_name="github.organization", string="Organization"
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

    @api.model
    def get_odoo_data_from_github(self, gh_data):
        res = super().get_odoo_data_from_github(gh_data)
        res.update(
            type=(res.get("type") or "").lower()
        )  # lowering type value to match selection value
        # set organization_id if the owner type is Organization
        # else set github_user_id if the type is User
        if gh_data.type == "Organization":
            # Fetch the organization owner
            org_id = self.env.context.get("github_organization_id", None)
            if not org_id:
                organization_obj = self.env["github.organization"]
                organization = organization_obj.get_from_id_or_create(gh_data=gh_data)
                org_id = organization.id
            res.update(organization_id=org_id)
        elif gh_data.type == "User":
            # Fetch the user owner
            partner_obj = self.env["res.partner"]
            github_user_partner = partner_obj.get_from_id_or_create(gh_data=gh_data)
            res.update(github_user_id=github_user_partner.id)
        return res

    @api.constrains("type", "organization_id", "github_user_id")
    def _check_type_organisation(self):
        owner_type_field_map = {
            "user": "user_id",
            "organization": "organization_id",
        }
        for owner in self.filtered(
            lambda o: not o.organization_id or not o.github_user_id
        ):
            fieldname = owner_type_field_map[owner.type]
            if not owner[fieldname]:
                raise ValidationError(
                    _(
                        "Field %(fname)s is required for owner of type %(owner_type)s",
                        **dict(
                            fname=self._fields[fieldname].string or fieldname,
                            owner_type=owner.type,
                        )
                    )
                )
