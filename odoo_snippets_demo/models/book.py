import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

LOW_STOCK_THRESHOLD = 5


class SnippetBook(models.Model):
    _name = "snippet.book"
    _description = "Book (snippet demo)"
    _order = "name"

    name = fields.Char(required=True)
    isbn = fields.Char(string="ISBN")
    author_id = fields.Many2one("res.partner", string="Author")
    price = fields.Float(digits="Product Price")
    quantity = fields.Integer(string="Quantity in Stock")
    needs_restock = fields.Boolean(readonly=True, help="Set by the scheduled action.")

    # --- Champ calculé STOCKÉ ------------------------------------------------
    # store=True : la valeur est écrite en base, donc triable / filtrable / groupable.
    # @api.depends est obligatoire : il dit à l'ORM quand recalculer.
    total_value = fields.Float(compute="_compute_total_value", store=True)

    # --- Champ calculé NON STOCKÉ --------------------------------------------
    # Recalculé à chaque lecture, rien en base. Pas de recherche possible
    # sans méthode `search=`.
    stock_status = fields.Selection(
        [("out", "Out of stock"), ("low", "Low stock"), ("ok", "In stock")],
        compute="_compute_stock_status",
    )

    # --- Contraintes SQL (Odoo 17 : _sql_constraints) ------------------------
    # Vérifiées par PostgreSQL ; en Odoo 19, remplacées par `models.Constraint`.
    _sql_constraints = [
        ("isbn_unique", "UNIQUE(isbn)", "This ISBN already exists."),
        ("quantity_positive", "CHECK(quantity >= 0)", "Quantity cannot be negative."),
    ]

    @api.depends("price", "quantity")
    def _compute_total_value(self):
        for book in self:
            book.total_value = book.price * book.quantity

    @api.depends("quantity")
    def _compute_stock_status(self):
        for book in self:
            if book.quantity <= 0:
                book.stock_status = "out"
            elif book.quantity < LOW_STOCK_THRESHOLD:
                book.stock_status = "low"
            else:
                book.stock_status = "ok"

    # --- Onchange -------------------------------------------------------------
    # Uniquement dans le formulaire (pas lors d'un create() en Python).
    # Préférer un champ calculé quand c'est possible ; l'onchange sert ici à
    # nettoyer une saisie et à afficher un avertissement.
    @api.onchange("isbn")
    def _onchange_isbn(self):
        if not self.isbn:
            return
        self.isbn = self.isbn.replace("-", "").replace(" ", "")
        if len(self.isbn) not in (10, 13):
            return {
                "warning": {
                    "title": _("Check the ISBN"),
                    "message": _("An ISBN has 10 or 13 characters."),
                }
            }

    # --- Contrainte Python ----------------------------------------------------
    # Pour les règles impossibles à écrire en SQL ; levée à chaque create/write
    # touchant les champs listés.
    @api.constrains("price")
    def _check_price(self):
        for book in self:
            if book.price < 0:
                raise ValidationError(_("The price of “%s” cannot be negative.", book.name))

    # --- Méthode appelée par l'action planifiée (data/ir_cron.xml) -----------
    @api.model
    def _cron_flag_low_stock(self):
        books = self.search([])
        low = books.filtered(lambda b: b.quantity < LOW_STOCK_THRESHOLD)
        low.needs_restock = True
        (books - low).needs_restock = False
        _logger.info("Low stock check: %s book(s) to restock", len(low))
