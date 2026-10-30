from odoo import api, fields, models


class SnippetBookRestockWizard(models.TransientModel):
    # TransientModel : enregistrements temporaires, purgés automatiquement.
    _name = "snippet.book.restock.wizard"
    _description = "Restock books (snippet demo)"

    book_ids = fields.Many2many("snippet.book", string="Books")
    quantity = fields.Integer(default=10, required=True)

    @api.model
    def default_get(self, fields_list):
        # Pré-remplit l'assistant avec les livres sélectionnés dans la liste.
        res = super().default_get(fields_list)
        if self.env.context.get("active_model") == "snippet.book":
            res["book_ids"] = [(6, 0, self.env.context.get("active_ids", []))]
        return res

    def action_restock(self):
        self.ensure_one()
        for book in self.book_ids:
            book.quantity += self.quantity
        return {"type": "ir.actions.act_window_close"}
