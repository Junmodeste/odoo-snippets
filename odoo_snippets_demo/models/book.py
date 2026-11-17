import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.fields import Domain

_logger = logging.getLogger(__name__)

LOW_STOCK_THRESHOLD = 5
VAT_RATE = 0.18  # TVA de 18 % (Côte d'Ivoire, Sénégal) ; exemple simplifié


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
    # sans méthode `search=` (voir _search_stock_status plus bas).
    stock_status = fields.Selection(
        [("out", "Out of stock"), ("low", "Low stock"), ("ok", "In stock")],
        compute="_compute_stock_status",
        search="_search_stock_status",
    )

    # --- Champ calculé MODIFIABLE (inverse=) ---------------------------------
    # Sans `inverse=`, un champ calculé est en lecture seule. La méthode
    # inverse reçoit la valeur saisie et met à jour les champs dont il dépend :
    # ici, saisir le prix TTC recalcule le prix HT (`price`). Dans un
    # formulaire, l'inverse ne s'exécute qu'à l'enregistrement (pas en direct).
    price_incl_vat = fields.Float(
        string="Price incl. VAT",
        digits="Product Price",
        compute="_compute_price_incl_vat",
        inverse="_inverse_price_incl_vat",
    )

    # --- Contraintes SQL (Odoo 19+ : models.Constraint) -----------------------
    # Vérifiées par PostgreSQL ; remplacent l'ancien `_sql_constraints`.
    _isbn_unique = models.Constraint("UNIQUE(isbn)", "This ISBN already exists.")
    _quantity_positive = models.Constraint("CHECK(quantity >= 0)", "Quantity cannot be negative.")

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

    # --- Recherche sur un champ calculé NON STOCKÉ ---------------------------
    # La méthode `search=` traduit la condition en domaine sur des champs
    # stockés. Odoo 19 normalise les opérateurs : `=` arrive en `in` avec un
    # ensemble de valeurs, et `!=` / `not in` sont déduits de `in` (négation).
    # Renvoyer NotImplemented pour tout autre opérateur.
    def _search_stock_status(self, operator, value):
        if operator != "in":
            return NotImplemented
        domains = {
            "out": [("quantity", "<=", 0)],
            "low": [("quantity", ">", 0), ("quantity", "<", LOW_STOCK_THRESHOLD)],
            "ok": [("quantity", ">=", LOW_STOCK_THRESHOLD)],
        }
        return Domain.OR(domains[status] for status in value if status in domains)

    @api.depends("price")
    def _compute_price_incl_vat(self):
        for book in self:
            book.price_incl_vat = book.price * (1 + VAT_RATE)

    def _inverse_price_incl_vat(self):
        for book in self:
            book.price = book.price_incl_vat / (1 + VAT_RATE)

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

    # --- Nom affiché (display_name) et recherche par plusieurs champs --------
    # `_rec_names_search` : champs interrogés quand on tape dans un champ
    # many2one ou dans la barre de recherche (name_search). Ici, on retrouve un
    # livre par son titre OU par son ISBN.
    _rec_names_search = ["name", "isbn"]

    # `_compute_display_name` remplace l'ancien `name_get` (supprimé en 17) :
    # le nom affiché partout (many2one, fil d'Ariane) devient « Titre (ISBN) ».
    @api.depends("name", "isbn")
    def _compute_display_name(self):
        for book in self:
            book.display_name = f"{book.name} ({book.isbn})" if book.isbn else book.name
