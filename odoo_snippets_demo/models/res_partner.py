from odoo import fields, models


class ResPartner(models.Model):
    # Héritage classique : on ajoute un champ au modèle existant.
    _inherit = "res.partner"

    favorite_book_id = fields.Many2one("snippet.book", string="Favorite Book")
