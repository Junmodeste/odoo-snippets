"""Appel de l'API externe d'Odoo 17 en XML-RPC (bibliothèque standard uniquement).

Usage :
    ODOO_URL=http://localhost:8069 ODOO_DB=odoo ODOO_USER=admin ODOO_PASSWORD=admin \
        python scripts/xmlrpc_client.py

Le mot de passe peut être remplacé par une clé API (Préférences > Sécurité du compte).
"""
import os
import xmlrpc.client

URL = os.environ.get("ODOO_URL", "http://localhost:8069")
DB = os.environ.get("ODOO_DB", "odoo")
USER = os.environ.get("ODOO_USER", "admin")
PASSWORD = os.environ.get("ODOO_PASSWORD", "admin")

# 1. Authentification : renvoie l'uid (False si identifiants invalides).
common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
print("Odoo", common.version()["server_version"])
uid = common.authenticate(DB, USER, PASSWORD, {})
if not uid:
    raise SystemExit("Authentification refusée")

# 2. Tous les appels métier passent par execute_kw(db, uid, password, modèle, méthode, args, kwargs).
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")


def call(model, method, *args, **kwargs):
    return models.execute_kw(DB, uid, PASSWORD, model, method, list(args), kwargs)


# Créer
book_id = call("snippet.book", "create", {"name": "Une si longue lettre", "price": 3500, "quantity": 2})
# Lire (search_read = search + read en un appel)
books = call("snippet.book", "search_read", [["id", "=", book_id]], fields=["name", "total_value", "stock_status"])
print(books)
# Modifier
call("snippet.book", "write", [book_id], {"quantity": 20})
# Compter
print("Livres :", call("snippet.book", "search_count", []))
# Supprimer
call("snippet.book", "unlink", [book_id])
