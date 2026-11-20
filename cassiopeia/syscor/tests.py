from django.contrib.auth.models import Group, User
from django.test import Client, TestCase
from django.urls import reverse


# Tests registration and account form responses.
# Testuje registraci a odpovědi formulářů účtu.
class AuthViewTests(TestCase):
    # Returns the first step for missing, invalid, or expired registration state.
    # Při chybějícím, neplatném nebo vypršelém stavu vrací první krok.
    def test_registration_recovers_from_invalid_steps(self):
        url = reverse("registration")
        for data in ({}, {"registration_step": "unknown"}, {"registration_step": "(step 1/2)"}):
            with self.subTest(data=data):
                self.assertContains(self.client.post(url, data), "(step 1/2)")
        response = self.client.post(url, {"registration_step": "(step 2/2)"})
        self.assertContains(response, "Your registration session has expired.")

    # Preserves the second step on validation errors and saves corrected profile details.
    # Při chybě zachovává druhý krok a ukládá opravené údaje profilu.
    def test_registration_validates_and_saves_profile(self):
        public_group = Group.objects.create(name="public")
        url = reverse("registration")
        password = "Example-password-618"
        response = self.client.post(url, {
            "registration_step": "(step 1/2)", "username": "Reader",
            "password": password, "password-again": password,
        })
        self.assertContains(response, "(step 2/2)")
        response = self.client.post(url, {"registration_step": "(step 2/2)", "email": "invalid"})
        self.assertContains(response, "Enter a valid email address.")
        self.assertIn("registration_user_id", self.client.session)
        response = self.client.post(url, {
            "registration_step": "(step 2/2)", "email": "reader@example.com", "first_name": "Eva",
        })
        self.assertRedirects(response, reverse("login"))
        user = User.objects.get(username="reader")
        self.assertEqual(user.email, "reader@example.com")
        self.assertEqual(user.first_name, "Eva")
        self.assertTrue(user.groups.filter(pk=public_group.pk).exists())
        self.assertNotIn("registration_user_id", self.client.session)

    # Rejects incomplete login and password changes without server errors.
    # Odmítá neúplné přihlášení a změnu hesla bez chyby serveru.
    def test_incomplete_account_forms_are_handled(self):
        self.assertContains(self.client.post(reverse("login"), {}), "Incorrect username or password")
        user = User.objects.create_user("reader", password="Example-password-618")
        self.client.force_login(user)
        for data in ({}, {"oldpassword": "Example-password-618"}):
            with self.subTest(data=data):
                self.assertContains(self.client.post(reverse("changepassword"), data), "This field is required.")
        user.refresh_from_db()
        self.assertTrue(user.check_password("Example-password-618"))

    # Requires a CSRF-protected POST before logging a user out.
    # Před odhlášením vyžaduje požadavek POST s ochranou CSRF.
    def test_logout_requires_post_and_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(User.objects.create_user("reader"))
        url = reverse("logout")
        self.assertEqual(client.get(url).status_code, 405)
        self.assertEqual(client.post(url).status_code, 403)
        self.assertIn("_auth_user_id", client.session)
        client.get(reverse("profile"))
        token = client.cookies["csrftoken"].value
        self.assertRedirects(client.post(url, {"csrfmiddlewaretoken": token}), reverse("home"))
        self.assertNotIn("_auth_user_id", client.session)
