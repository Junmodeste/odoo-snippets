# Odoo 20 Snippets

[![Odoo 20](https://img.shields.io/badge/Odoo-20.0-714B67)](https://www.odoo.com)
[![tests](https://github.com/Junmodeste/odoo-snippets/actions/workflows/tests.yml/badge.svg?branch=20.0)](https://github.com/Junmodeste/odoo-snippets/actions/workflows/tests.yml)
[![License: LGPL-3](https://img.shields.io/badge/License-LGPL--3-blue.svg)](LICENSE)

🇫🇷 [Français](#français) · 🇬🇧 [English](#english)

## Français

Une antisèche commentée en français des briques de code Odoo 20 les plus utilisées.
Tous les exemples vivent dans le module installable `odoo_snippets_demo` (un petit catalogue de livres), couvert par des tests qui prouvent qu'ils fonctionnent.

### Sommaire

| # | Exemple | Fichier |
|---|---|---|
| 1 | Champ calculé **stocké** (`store=True`) | [models/book.py#L25](odoo_snippets_demo/models/book.py#L25) |
| 2 | Champ calculé **non stocké** | [models/book.py#L30](odoo_snippets_demo/models/book.py#L30) |
| 3 | Onchange avec avertissement | [models/book.py#L95](odoo_snippets_demo/models/book.py#L95) |
| 4 | Contrainte **Python** (`@api.constrains`) | [models/book.py#L112](odoo_snippets_demo/models/book.py#L112) |
| 5 | Contraintes **SQL** (`models.Constraint`, depuis la 19) | [models/book.py#L51](odoo_snippets_demo/models/book.py#L51) |
| 6 | Assistant (`TransientModel`) + action liée | [wizards/book_restock_wizard.py](odoo_snippets_demo/wizards/book_restock_wizard.py), [vue](odoo_snippets_demo/wizards/book_restock_wizard_views.xml) |
| 7 | Action planifiée (`ir.cron`) | [data/ir_cron.xml](odoo_snippets_demo/data/ir_cron.xml), [méthode](odoo_snippets_demo/models/book.py#L121) |
| 8 | Rapport QWeb PDF | [report/book_report.xml](odoo_snippets_demo/report/book_report.xml) |
| 9 | Héritage de vue (`inherit_id` + `xpath`) | [views/res_partner_views.xml](odoo_snippets_demo/views/res_partner_views.xml), [modèle](odoo_snippets_demo/models/res_partner.py) |
| 10 | Vues `<list>`, formulaire, recherche (`invisible` direct) | [views/book_views.xml](odoo_snippets_demo/views/book_views.xml) |
| 11 | API externe en **XML-RPC** | [scripts/xmlrpc_client.py](scripts/xmlrpc_client.py) |
| 12 | Tests de chaque exemple | [tests/test_snippets.py](odoo_snippets_demo/tests/test_snippets.py) |
| 13 | Recherche sur un champ calculé **non stocké** (`search=`) + filtres | [models/book.py#L71](odoo_snippets_demo/models/book.py#L71), [vue](odoo_snippets_demo/views/book_views.xml) |
| 14 | Champ calculé **modifiable** (`inverse=`) : prix TTC ↔ prix HT | [models/book.py#L39](odoo_snippets_demo/models/book.py#L39) |
| 15 | Nom affiché (`_compute_display_name`) + recherche par titre ou ISBN (`_rec_names_search`) | [models/book.py#L130](odoo_snippets_demo/models/book.py#L130) |
| 16 | **Multi-société** : champ `company_id` + restriction `ir.access` (ligne sans groupe avec `domain`, ex-`ir.rule`) | [models/book.py#L143](odoo_snippets_demo/models/book.py#L143), [restriction](odoo_snippets_demo/security/ir.access.csv) |

![Rapport QWeb](odoo_snippets_demo/static/description/report.png)

### Prérequis

- Odoo 20 (Community ou Enterprise) ; seuls `base` et `web` sont requis
- Python 3 pour le script XML-RPC (bibliothèque standard uniquement)

### Installation

1. Copiez `odoo_snippets_demo` dans votre chemin d'addons.
2. Mettez à jour la liste des applications puis installez **Odoo Snippets Demo** (menu *Snippets*).
3. Optionnel : `ODOO_URL=http://localhost:8069 ODOO_DB=ma_base ODOO_USER=admin ODOO_PASSWORD=*** python scripts/xmlrpc_client.py`

Lancer les tests : `odoo -d test -i odoo_snippets_demo --test-enable --stop-after-init`

### Versions supportées

Une branche par version d'Odoo : [`20.0`](https://github.com/Junmodeste/odoo-snippets/tree/20.0) (cette branche), [`19.0`](https://github.com/Junmodeste/odoo-snippets/tree/19.0), [`18.0`](https://github.com/Junmodeste/odoo-snippets/tree/18.0), [`17.0`](https://github.com/Junmodeste/odoo-snippets/tree/17.0). Tests automatisés exécutés en CI sur Odoo 20 Community (image `odoo:20`, 20.0-20261112 en local) + `postgres:16`.

Changements apportés pour Odoo 20 : les droits d'accès passent de `ir.model.access.csv` à [`security/ir.access.csv`](odoo_snippets_demo/security/ir.access.csv) (modèle `ir.access` : colonne `operation` = sous-ensemble de `crud`, colonne `domain` facultative, qui remplace aussi les règles d'enregistrement) ; le champ `report_file` d'`ir.actions.report` n'existe plus ; dans le formulaire partenaire, `vat` est dans `div[@name='identifiers']`, on insère donc après ce bloc.

### Licence

[LGPL-3](LICENSE)

### Auteur

Koffi Modeste Junior — [@Junmodeste](https://github.com/Junmodeste)

## English

A commented cheat sheet (in French) of the most used Odoo 20 code patterns.
Every example lives in the installable `odoo_snippets_demo` module (a small book catalog), with tests proving they work.

### Contents

| # | Example | File |
|---|---|---|
| 1 | **Stored** computed field | [models/book.py#L25](odoo_snippets_demo/models/book.py#L25) |
| 2 | **Non-stored** computed field | [models/book.py#L30](odoo_snippets_demo/models/book.py#L30) |
| 3 | Onchange with warning | [models/book.py#L95](odoo_snippets_demo/models/book.py#L95) |
| 4 | **Python** constraint | [models/book.py#L112](odoo_snippets_demo/models/book.py#L112) |
| 5 | **SQL** constraints (`models.Constraint`, since 19) | [models/book.py#L51](odoo_snippets_demo/models/book.py#L51) |
| 6 | Wizard (`TransientModel`) + bound action | [wizards/book_restock_wizard.py](odoo_snippets_demo/wizards/book_restock_wizard.py) |
| 7 | Scheduled action (`ir.cron`) | [data/ir_cron.xml](odoo_snippets_demo/data/ir_cron.xml) |
| 8 | QWeb PDF report | [report/book_report.xml](odoo_snippets_demo/report/book_report.xml) |
| 9 | View inheritance (`inherit_id` + `xpath`) | [views/res_partner_views.xml](odoo_snippets_demo/views/res_partner_views.xml) |
| 10 | `<list>`, form and search views | [views/book_views.xml](odoo_snippets_demo/views/book_views.xml) |
| 11 | External **XML-RPC** API | [scripts/xmlrpc_client.py](scripts/xmlrpc_client.py) |
| 12 | Tests for every example | [tests/test_snippets.py](odoo_snippets_demo/tests/test_snippets.py) |
| 13 | Searching a **non-stored** computed field (`search=`) + filters | [models/book.py#L71](odoo_snippets_demo/models/book.py#L71), [view](odoo_snippets_demo/views/book_views.xml) |
| 14 | **Editable** computed field (`inverse=`): price incl. VAT ↔ price | [models/book.py#L39](odoo_snippets_demo/models/book.py#L39) |
| 15 | Display name (`_compute_display_name`) + search by title or ISBN (`_rec_names_search`) | [models/book.py#L130](odoo_snippets_demo/models/book.py#L130) |
| 16 | **Multi-company**: `company_id` field + `ir.access` restriction (row without group, with `domain`; formerly `ir.rule`) | [models/book.py#L143](odoo_snippets_demo/models/book.py#L143), [restriction](odoo_snippets_demo/security/ir.access.csv) |

### Requirements

- Odoo 20 (Community or Enterprise); only `base` and `web` are required
- Python 3 for the XML-RPC script (standard library only)

### Installation

1. Copy `odoo_snippets_demo` into your addons path.
2. Update the apps list and install **Odoo Snippets Demo** (*Snippets* menu).
3. Optional: `ODOO_URL=http://localhost:8069 ODOO_DB=my_db ODOO_USER=admin ODOO_PASSWORD=*** python scripts/xmlrpc_client.py`

### Supported versions

One branch per Odoo version: [`20.0`](https://github.com/Junmodeste/odoo-snippets/tree/20.0) (this branch), [`19.0`](https://github.com/Junmodeste/odoo-snippets/tree/19.0), [`18.0`](https://github.com/Junmodeste/odoo-snippets/tree/18.0), [`17.0`](https://github.com/Junmodeste/odoo-snippets/tree/17.0). Automated tests run in CI on Odoo 20 Community (`odoo:20` image, 20.0-20261112 locally) + `postgres:16`.

Changes made for Odoo 20: access rights move from `ir.model.access.csv` to [`security/ir.access.csv`](odoo_snippets_demo/security/ir.access.csv) (`ir.access` model: `operation` column = subset of `crud`, optional `domain` column, which also replaces record rules); the `report_file` field of `ir.actions.report` is gone; in the partner form, `vat` sits inside `div[@name='identifiers']`, so we insert after that block.

### License

[LGPL-3](LICENSE)

### Author

Koffi Modeste Junior — [@Junmodeste](https://github.com/Junmodeste)
