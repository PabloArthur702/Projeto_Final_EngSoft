import unittest
from app import app, db, User

class TestUserModel(unittest.TestCase):
    def setUp(self):
        # Configura o ambiente de teste
        self.app = app.test_client()
        self.app.testing = True
        with app.app_context():
            db.create_all()

    def tearDown(self):
        # Limpa o banco de dados após cada teste
        with app.app_context():
            db.session.remove()
            db.drop_all()
    def test_create_user(self):
        # Testa a criação de um usuário com dados válidos
        with app.app_context():
            user = User(username="testuser", password="hashed_password")
            db.session.add(user)
            db.session.commit()

            # Verifica se o usuário foi adicionado ao banco
            user_in_db = User.query.filter_by(username="testuser").first()
            self.assertIsNotNone(user_in_db)
            self.assertEqual(user_in_db.username, "testuser")
            self.assertEqual(user_in_db.password, "hashed_password")

    def test_username_uniqueness(self):
        # Testa a unicidade do nome de usuário
        with app.app_context():
            user1 = User(username="uniqueuser", password="password1")
            user2 = User(username="uniqueuser", password="password2")
            db.session.add(user1)
            db.session.commit()

            # Tentar adicionar o segundo usuário com o mesmo nome deve gerar um erro
            with self.assertRaises(Exception):
                db.session.add(user2)
                db.session.commit()

    def test_required_fields(self):
        # Testa a validação de campos obrigatórios
        with app.app_context():
            user_missing_username = User(username=None, password="password")
            user_missing_password = User(username="userwithoutpassword", password=None)

            # Tentar adicionar usuários com campos obrigatórios faltando deve falhar
            with self.assertRaises(Exception):
                db.session.add(user_missing_username)
                db.session.commit()

            with self.assertRaises(Exception):
                db.session.add(user_missing_password)
                db.session.commit()

if __name__ == "__main__":
    unittest.main()