from psycopg2 import IntegrityError

from odoo.exceptions import ValidationError
from odoo.tests import Form, TransactionCase, tagged
from odoo.tools import mute_logger


@tagged("post_install", "-at_install")
class TestSnippets(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Book = cls.env["snippet.book"]
        cls.book = cls.Book.create({"name": "Les Soleils des indépendances", "price": 5000, "quantity": 3})

    def test_stored_compute(self):
        self.assertEqual(self.book.total_value, 15000)
        self.book.quantity = 4
        self.assertEqual(self.book.total_value, 20000)
        # Stocké : utilisable dans un domaine de recherche.
        self.assertIn(self.book, self.Book.search([("total_value", "=", 20000)]))

    def test_non_stored_compute(self):
        self.assertEqual(self.book.stock_status, "low")
        self.book.quantity = 0
        self.assertEqual(self.book.stock_status, "out")
        self.book.quantity = 50
        self.assertEqual(self.book.stock_status, "ok")

    def test_onchange(self):
        with Form(self.Book) as form:
            form.name = "Allah n'est pas obligé"
            form.isbn = "978-2-02-041519-5"
            self.assertEqual(form.isbn, "9782020415195")

    def test_python_constraint(self):
        with self.assertRaises(ValidationError):
            self.book.price = -1

    def test_sql_constraints(self):
        self.book.isbn = "9782020415195"
        with mute_logger("odoo.sql_db"), self.assertRaises(IntegrityError), self.cr.savepoint():
            self.Book.create({"name": "Doublon", "isbn": "9782020415195"})
        with mute_logger("odoo.sql_db"), self.assertRaises(IntegrityError), self.cr.savepoint():
            self.Book.create({"name": "Stock négatif", "quantity": -1})

    def test_wizard(self):
        wizard = self.env["snippet.book.restock.wizard"].with_context(
            active_model="snippet.book", active_ids=self.book.ids,
        ).create({"quantity": 7})
        self.assertEqual(wizard.book_ids, self.book)
        wizard.action_restock()
        self.assertEqual(self.book.quantity, 10)

    def test_cron(self):
        full = self.Book.create({"name": "Stock plein", "quantity": 100, "needs_restock": True})
        # Exécute le code de l'action planifiée dans la transaction du test
        # (method_direct_trigger passe par le planificateur et son propre traitement).
        cron = self.env.ref("odoo_snippets_demo.snippet_book_cron_low_stock")
        # Odoo 17 : sans numbercall = -1, l'action ne tournerait qu'une fois.
        self.assertEqual(cron.numbercall, -1)
        cron.ir_actions_server_id.run()
        self.assertTrue(self.book.needs_restock)
        self.assertFalse(full.needs_restock)

    def test_report(self):
        html, _type = self.env["ir.actions.report"]._render_qweb_html(
            "odoo_snippets_demo.snippet_book_report_action", self.book.ids,
        )
        self.assertIn("Les Soleils des indépendances", html.decode())

    def test_view_inheritance(self):
        partner = self.env["res.partner"].create({"name": "Ahmadou Kourouma"})
        with Form(partner) as form:
            form.favorite_book_id = self.book
        self.assertEqual(partner.favorite_book_id, self.book)
