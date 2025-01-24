import unittest
from flask_bcrypt import Bcrypt

class TestBcrypt(unittest.TestCase):
    def setUp(self):
        # Instancia o Bcrypt para teste
        self.bcrypt = Bcrypt()

    def test_generate_password_hash(self):
        # Testa se o hash é gerado corretamente
        password = "minha_senha_secreta"
        hashed = self.bcrypt.generate_password_hash(password).decode('utf-8')
        self.assertIsInstance(hashed, str)
        self.assertNotEqual(password, hashed)

    def test_check_password_hash(self):
        # Testa se o hash pode ser validado corretamente
        password = "minha_senha_secreta"
        hashed = self.bcrypt.generate_password_hash(password).decode('utf-8')
        self.assertTrue(self.bcrypt.check_password_hash(hashed, password))
        self.assertFalse(self.bcrypt.check_password_hash(hashed, "senha_errada"))

    def test_hashes_are_unique(self):
        # Testa se hashes para a mesma senha são diferentes
        password = "minha_senha_secreta"
        hash1 = self.bcrypt.generate_password_hash(password).decode('utf-8')
        hash2 = self.bcrypt.generate_password_hash(password).decode('utf-8')
        self.assertNotEqual(hash1, hash2)

if __name__ == "__main__":
    unittest.main()