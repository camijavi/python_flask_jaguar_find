import os
import unittest
import tempfile
import sqlite3
import json

from backend.app import app
from backend.config import Config
from backend.database import initDb


class TestVisitorValidation(unittest.TestCase):
    def setUp(self):
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.temp_db_fd)
        
        # Save original db path and configure temp db
        self.original_db_path = Config.DATABASE_PATH
        Config.DATABASE_PATH = self.temp_db_path
        
        # Initialize isolated test database
        initDb(dbPath=self.temp_db_path, seedSampleData=True)
        
        app.config["TESTING"] = True
        app.config["DB_PATH"] = self.temp_db_path
        self.client = app.test_client()

    def tearDown(self):
        Config.DATABASE_PATH = self.original_db_path
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)

    # 1. REQUIRED FIELDS VALIDATION
    def test_visitor_signup_missing_fullname(self):
        res = self.client.post("/api/auth/signup", json={
            "userTypeId": 3,
            "fullName": "   ",
            "govermentId": "001-111199-0001A",
            "phoneNumber": "88881111",
            "email": "test@visitor.com"
        })
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertEqual(data.get("field"), "nombre")

    def test_signup_cedula_inputs_have_matching_length_limits(self):
        for role in ("visitante", "colaborador"):
            with self.subTest(role=role):
                res = self.client.get(f"/auth/signup?rol={role}")
                self.assertEqual(res.status_code, 200)
                self.assertIn('id="cedula"', res.get_data(as_text=True))
                self.assertIn('minlength="14" maxlength="16"', res.get_data(as_text=True))

    def test_password_visibility_toggle_is_rendered_on_auth_forms(self):
        for route in (
            "/auth/signup?rol=colaborador",
            "/auth/signin?rol=colaborador",
            "/admin/adminsignin",
        ):
            with self.subTest(route=route):
                res = self.client.get(route)
                self.assertEqual(res.status_code, 200)
                html = res.get_data(as_text=True)
                self.assertIn('type="button" data-password-toggle', html)
                self.assertIn('aria-controls="password"', html)
                self.assertIn('data-i18n-aria-label="auth.show_password"', html)
                self.assertIn('pl-11 pr-12', html)
                self.assertIn("passwordVisibilityToggle.js", html)

    def test_visitor_signup_missing_cedula(self):
        res = self.client.post("/api/auth/signup", json={
            "userTypeId": 3,
            "fullName": "Visitante Valido",
            "govermentId": "",
            "phoneNumber": "88881111",
            "email": "test@visitor.com"
        })
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertEqual(data.get("field"), "cedula")

    def test_visitor_signup_missing_phone(self):
        res = self.client.post("/api/auth/signup", json={
            "userTypeId": 3,
            "fullName": "Visitante Valido",
            "govermentId": "001-111199-0001A",
            "phoneNumber": "",
            "email": "test@visitor.com"
        })
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertEqual(data.get("field"), "telefono")

    def test_visitor_signup_missing_email(self):
        res = self.client.post("/api/auth/signup", json={
            "userTypeId": 3,
            "fullName": "Visitante Valido",
            "govermentId": "001-111199-0001A",
            "phoneNumber": "88881111",
            "email": ""
        })
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertEqual(data.get("field"), "correoPersonal")

    # 2. CEDULA FORMAT VALIDATION
    def test_visitor_signup_invalid_cedula_format(self):
        invalid_cedulas = [
            "123",
            "001111990001A",       # shorter than the minimum length
            "001-111199-00001AA",   # longer than the maximum length
            "001-111199-0001",      # missing trailing letter
            "001-AAAAAA-0001A",     # letters in date
            "01-111199-0001A",      # only 2 digits in municipality
            "001-111199-00001A",    # too many digits in sequence
            "001-111199-00011",     # number instead of letter
        ]
        for ced in invalid_cedulas:
            res = self.client.post("/api/auth/signup", json={
                "userTypeId": 3,
                "fullName": "Visitante Valido",
                "govermentId": ced,
                "phoneNumber": "88881111",
                "email": "test@visitor.com"
            })
            self.assertEqual(res.status_code, 400, f"Cedula '{ced}' should have been rejected")
            data = res.get_json()
            self.assertFalse(data["success"])
            self.assertEqual(data.get("field"), "cedula")

    def test_database_rejects_government_ids_outside_length_bounds(self):
        conn = sqlite3.connect(self.temp_db_path)
        try:
            for invalid_id in ("001111990001A", "001-111199-00001AA"):
                with self.subTest(government_id=invalid_id):
                    with self.assertRaises(sqlite3.IntegrityError):
                        conn.execute(
                            "INSERT INTO UserTbl (UserTypeId, FullName, GovermentId) VALUES (2, ?, ?);",
                            ("Invalid Length", invalid_id)
                        )
                    conn.rollback()
        finally:
            conn.close()

    def test_visitor_signup_valid_cedula_format(self):
        res = self.client.post("/api/auth/signup", json={
            "userTypeId": 3,
            "fullName": "Visitante Con Cedula",
            "govermentId": "001-111199-0001A",
            "phoneNumber": "88881111",
            "email": "test1@visitor.com"
        })
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["user"]["GovermentId"], "001-111199-0001A")

    def test_visitor_signup_cedula_without_hyphens_normalized(self):
        res = self.client.post("/api/auth/signup", json={
            "userTypeId": 3,
            "fullName": "Visitante Sin Guiones",
            "govermentId": "0011111990002b",
            "phoneNumber": "88882222",
            "email": "test2@visitor.com"
        })
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertTrue(data["success"])
        # Should normalize to standard 001-111199-0002B
        self.assertEqual(data["user"]["GovermentId"], "001-111199-0002B")

    # 3. PHONE NUMBER RULES (STRIP NON-NUMERIC, ALLOW DIGITS ONLY)
    def test_visitor_signup_phone_stripping_and_digits_only(self):
        res = self.client.post("/api/auth/signup", json={
            "userTypeId": 3,
            "fullName": "Visitante Telefono",
            "govermentId": "001-111199-0003C",
            "phoneNumber": "+505 (8888) 33-33",
            "email": "test3@visitor.com"
        })
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertTrue(data["success"])
        # Stored phone must contain digits only
        self.assertEqual(data["user"]["PhoneNumber"], "50588883333")
        self.assertTrue(data["user"]["PhoneNumber"].isdigit())

    def test_visitor_signup_phone_all_symbols_rejected(self):
        res = self.client.post("/api/auth/signup", json={
            "userTypeId": 3,
            "fullName": "Visitante Telefono Simbolos",
            "govermentId": "001-111199-0004D",
            "phoneNumber": "--- () +++",
            "email": "test_sym@visitor.com"
        })
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertEqual(data.get("field"), "telefono")

    def test_visitor_signup_phone_reject_letters(self):
        res = self.client.post("/api/auth/signup", json={
            "userTypeId": 3,
            "fullName": "Visitante Telefono Letras",
            "govermentId": "001-111199-0004D",
            "phoneNumber": "8888abcd",
            "email": "test4@visitor.com"
        })
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertEqual(data.get("field"), "telefono")

    def test_visitor_signup_phone_too_short(self):
        res = self.client.post("/api/auth/signup", json={
            "userTypeId": 3,
            "fullName": "Visitante Telefono Corto",
            "govermentId": "001-111199-0005E",
            "phoneNumber": "123",
            "email": "test5@visitor.com"
        })
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertEqual(data.get("field"), "telefono")

    # 4. EMAIL VALIDATION (STANDARD EMAIL FORMAT WITH @ AND VALID DOMAIN)
    def test_visitor_signup_invalid_email_format(self):
        invalid_emails = [
            "notanemail",
            "user@",
            "@domain.com",
            "user@domain",          # missing TLD extension
            "user@.com",            # missing domain name
            "user@domain.",         # trailing dot without TLD
            "user@domain.c",        # TLD too short (< 2 letters)
            "user space@domain.com"
        ]
        for em in invalid_emails:
            res = self.client.post("/api/auth/signup", json={
                "userTypeId": 3,
                "fullName": "Visitante Correo Invalido",
                "govermentId": "001-111199-0006F",
                "phoneNumber": "88886666",
                "email": em
            })
            self.assertEqual(res.status_code, 400, f"Email '{em}' should have been rejected")
            data = res.get_json()
            self.assertFalse(data["success"])
            self.assertEqual(data.get("field"), "correoPersonal")

    def test_visitor_signup_valid_email(self):
        res = self.client.post("/api/auth/signup", json={
            "userTypeId": 3,
            "fullName": "Visitante Correo Valido",
            "govermentId": "001-111199-0007G",
            "phoneNumber": "88887777",
            "email": "usuario.valido@externo.org"
        })
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["user"]["Email"], "usuario.valido@externo.org")

    # 5. PASSWORDLESS LOGIN FOR REGISTERED VISITOR
    def test_visitor_login_with_cedula_and_phone(self):
        # Register a visitor
        signup_res = self.client.post("/api/auth/signup", json={
            "userTypeId": 3,
            "fullName": "Visitante Acceso",
            "govermentId": "001-111199-0008H",
            "phoneNumber": "88888888",
            "email": "acceso@visitante.com"
        })
        self.assertEqual(signup_res.status_code, 201)

        # Login using Cédula
        login_res_cedula = self.client.post("/api/auth/login", json={
            "userTypeId": 3,
            "identifier": "001-111199-0008H"
        })
        self.assertEqual(login_res_cedula.status_code, 200)
        self.assertTrue(login_res_cedula.get_json()["success"])

        # Login using Phone Number
        login_res_phone = self.client.post("/api/auth/login", json={
            "userTypeId": 3,
            "identifier": "88888888"
        })
        self.assertEqual(login_res_phone.status_code, 200)
        self.assertTrue(login_res_phone.get_json()["success"])


    # 6. ADMIN CREATING VISITOR VALIDATION
    def test_admin_create_visitor_validation(self):
        # Login as admin first
        login_res = self.client.post("/api/auth/login", json={
            "userTypeId": 4,
            "identifier": "admin@uamv.edu.ni",
            "password": "admin123"
        })
        self.assertEqual(login_res.status_code, 200)

        # Missing fields
        res_fail = self.client.post("/api/admin/users", json={
            "userTypeId": 3,
            "fullName": "Admin Visitor",
            "cedula": "001-111199-0009I",
            "phoneNumber": "88889999",
            "email": "invalid-email"
        })
        self.assertEqual(res_fail.status_code, 400)

        # Valid visitor creation via admin
        res_ok = self.client.post("/api/admin/users", json={
            "userTypeId": 3,
            "fullName": "Admin Visitor Valid",
            "cedula": "001-111199-0009I",
            "phoneNumber": "+505 8888 9999",
            "email": "admin_visitor@test.com"
        })
        self.assertEqual(res_ok.status_code, 201)
        self.assertEqual(res_ok.get_json()["user"]["PhoneNumber"], "50588889999")


if __name__ == "__main__":
    unittest.main()
