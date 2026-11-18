from lxml import etree
from psycopg2 import IntegrityError

from odoo.exceptions import AccessError, ValidationError
from odoo.tests import Form, TransactionCase, new_test_user, tagged
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

    def test_search_non_stored_compute(self):
        out = self.Book.create({"name": "Épuisé", "quantity": 0})
        full = self.Book.create({"name": "Stock plein", "quantity": 100})
        books = self.book | out | full
        domain = [("id", "in", books.ids)]
        self.assertEqual(self.Book.search(domain + [("stock_status", "=", "low")]), self.book)
        self.assertEqual(self.Book.search(domain + [("stock_status", "in", ["out", "ok"])]), out | full)
        self.assertEqual(self.Book.search(domain + [("stock_status", "!=", "out")]), self.book | full)

    def test_inverse_compute(self):
        self.assertAlmostEqual(self.book.price_incl_vat, 5900)
        # Écrire le champ calculé appelle la méthode inverse, qui met à jour price.
        self.book.price_incl_vat = 11800
        self.assertAlmostEqual(self.book.price, 10000)
        self.assertEqual(self.book.total_value, 30000)
        # Dans le formulaire, l'inverse ne s'exécute qu'à l'enregistrement :
        # price garde son ancienne valeur tant que le formulaire est ouvert.
        with Form(self.book) as form:
            form.price_incl_vat = 2360
            self.assertAlmostEqual(form.price, 10000)
        self.assertAlmostEqual(self.book.price, 2000)

    def test_display_name_and_name_search(self):
        self.assertEqual(self.book.display_name, "Les Soleils des indépendances")
        self.book.isbn = "9782020259766"
        self.assertEqual(self.book.display_name, "Les Soleils des indépendances (9782020259766)")
        # name_search interroge `_rec_names_search` : titre ou ISBN.
        self.assertIn(self.book.id, [r[0] for r in self.Book.name_search("0259766")])
        self.assertIn(self.book.id, [r[0] for r in self.Book.name_search("Soleils")])
        self.assertIn(self.book, self.Book.search([("display_name", "ilike", "9782020")]))

    def test_multi_company_rule(self):
        company_a = self.env.company
        company_b = self.env["res.company"].create({"name": "Société B"})
        self.assertEqual(self.book.company_id, company_a)
        book_b = self.Book.create({"name": "Livre B", "company_id": company_b.id})
        shared = self.Book.create({"name": "Livre partagé", "company_id": False})
        user = new_test_user(self.env, login="snippet_mc", company_id=company_a.id, company_ids=company_a.ids)
        domain = [("id", "in", (self.book | book_b | shared).ids)]
        # La règle masque le livre de la société B à un utilisateur de la société A.
        self.assertEqual(self.Book.with_user(user).search(domain), self.book | shared)
        with self.assertRaises(AccessError):
            book_b.with_user(user).read(["name"])
        # Avec accès aux deux sociétés actives, les trois livres sont visibles.
        user.company_ids = company_a | company_b
        both = self.Book.with_user(user).with_context(allowed_company_ids=[company_a.id, company_b.id])
        self.assertEqual(both.search(domain), self.book | book_b | shared)

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
        self.env.ref("odoo_snippets_demo.snippet_book_cron_low_stock").ir_actions_server_id.run()
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
        # Odoo 20 : le champ est inséré après le bloc des identifiants, pas dans la ligne de la TVA
        arch = etree.fromstring(self.env["res.partner"].get_view(view_type="form")["arch"])
        self.assertTrue(arch.xpath("//div[@name='identifiers']/following-sibling::field[@name='favorite_book_id']"))
        self.assertFalse(arch.xpath("//div[@id='vat_div']//field[@name='favorite_book_id']"))
