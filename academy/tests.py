from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Note


User = get_user_model()


class PublicNavigationTests(TestCase):
    def test_primary_public_pages_render(self):
        for route in (
            "home",
            "paths",
            "themes",
            "repertoires",
            "official_materials",
            "privacy",
            "essay_examples",
            "writing_workshop",
            "login",
        ):
            with self.subTest(route=route):
                response = self.client.get(reverse(route))
                self.assertEqual(response.status_code, 200)

    def test_authenticated_home_redirects_to_dashboard(self):
        user = User.objects.create_user(
            email="estudante@example.com", password="UmaSenhaMuitoForte!2026", first_name="Lia"
        )
        self.client.force_login(user)
        response = self.client.get(reverse("home"))
        self.assertRedirects(response, reverse("dashboard"))

    def test_brand_link_points_to_dashboard_for_authenticated_user(self):
        user = User.objects.create_user(
            email="estudante@example.com", password="UmaSenhaMuitoForte!2026", first_name="Lia"
        )
        self.client.force_login(user)
        response = self.client.get(reverse("privacy"))
        self.assertContains(response, 'class="brand" href="/app/"')

    def test_private_pages_redirect_to_login(self):
        for route in ("dashboard", "notes_home", "profile"):
            with self.subTest(route=route):
                response = self.client.get(reverse(route))
                self.assertRedirects(response, f"{reverse('login')}?next={reverse(route)}")

    @override_settings(REDAWAY_REGISTRATION_ENABLED=False)
    def test_registration_is_closed_when_disabled(self):
        self.assertEqual(self.client.get(reverse("register")).status_code, 404)


class AccountAndNotesTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="aluna@example.com", password="UmaSenhaMuitoForte!2026", first_name="Ana"
        )
        self.other = User.objects.create_user(
            email="outra@example.com", password="UmaSenhaMuitoForte!2026", first_name="Bia"
        )

    def test_email_is_normalized_and_case_insensitive_unique(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.create_user(
                email="ALUNA@EXAMPLE.COM", password="UmaSenhaMuitoForte!2026", first_name="Outra"
            )

    @override_settings(REDAWAY_REGISTRATION_ENABLED=True)
    def test_registration_rejects_duplicate_email_ignoring_case(self):
        response = self.client.post(reverse("register"), {
            "first_name": "Ana",
            "last_name": "",
            "email": "ALUNA@EXAMPLE.COM",
            "password1": "UmaSenhaMuitoForte!2026",
            "password2": "UmaSenhaMuitoForte!2026",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Este e-mail já está cadastrado")
        self.assertEqual(User.objects.filter(email__iexact="aluna@example.com").count(), 1)

    def test_notes_are_private_and_sanitized(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse("note_new"), {
            "title": "Minha nota", "topic": "ENEM",
            "body": '<p>ideia <mark>importante</mark></p><script>alert(1)</script>',
        })
        note = Note.objects.get(user=self.owner)
        self.assertRedirects(response, reverse("note_edit", args=(note.pk,)))
        self.assertIn("<mark>importante</mark>", note.body)
        self.assertNotIn("<script", note.body)

        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse("note_edit", args=(note.pk,))).status_code, 404)
        self.assertEqual(self.client.post(reverse("note_delete", args=(note.pk,))).status_code, 404)
        self.assertTrue(Note.objects.filter(pk=note.pk, user=self.owner).exists())

    def test_note_autosave_uses_json_response(self):
        note = Note.objects.create(user=self.owner, title="Rascunho")
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("note_edit", args=(note.pk,)),
            {"title": "Rascunho salvo", "topic": "argumentação", "body": "<p>Nova ideia</p>"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)
        note.refresh_from_db()
        self.assertJSONEqual(response.content, {"ok": True, "saved_at": note.updated_at.strftime("%H:%M")})
        self.assertEqual(note.title, "Rascunho salvo")

    def test_note_delete_requires_post(self):
        note = Note.objects.create(user=self.owner, title="Remover")
        self.client.force_login(self.owner)
        response = self.client.get(reverse("note_delete", args=(note.pk,)))
        self.assertEqual(response.status_code, 405)
        self.assertTrue(Note.objects.filter(pk=note.pk).exists())
