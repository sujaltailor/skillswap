from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import ExchangeRequest, Profile, Skill


@override_settings(SECURE_SSL_REDIRECT=False)
class SkillSwapWorkflowTests(TestCase):
    def setUp(self):
        self.python = Skill.objects.create(name="Python")
        self.alice = User.objects.create_user(username="alice", first_name="Alice", password="StrongPass123")
        self.bob = User.objects.create_user(username="bob", first_name="Bob", password="StrongPass123")
        self.alice_profile = Profile.objects.create(user=self.alice)
        self.bob_profile = Profile.objects.create(user=self.bob)
        self.alice_profile.skills_to_teach.add(self.python)
        self.bob_profile.skills_to_teach.add(self.python)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))

        self.assertRedirects(
            response,
            f'{reverse("login")}?next={reverse("dashboard")}',
            fetch_redirect_response=False,
        )

    def test_search_does_not_show_current_user(self):
        self.client.force_login(self.alice)

        response = self.client.get(reverse("find_skills"), {"q": "Python"})

        self.assertContains(response, "Bob")
        self.assertNotContains(response, "Alice")

    def test_user_cannot_request_their_own_profile(self):
        self.client.force_login(self.alice)

        response = self.client.post(
            reverse("send_request", args=[self.alice_profile.pk]),
            {"message": "Hello"},
        )

        self.assertRedirects(response, reverse("dashboard"))
        self.assertFalse(ExchangeRequest.objects.exists())

    def test_duplicate_pending_request_is_not_created(self):
        self.client.force_login(self.alice)
        url = reverse("send_request", args=[self.bob_profile.pk])

        self.client.post(url, {"message": "First"})
        self.client.post(url, {"message": "Second"})

        self.assertEqual(ExchangeRequest.objects.count(), 1)

    def test_only_receiver_can_accept_request(self):
        exchange = ExchangeRequest.objects.create(
            sender=self.alice_profile,
            receiver=self.bob_profile,
        )
        self.client.force_login(self.alice)

        self.client.post(reverse("accept_request", args=[exchange.pk]))

        exchange.refresh_from_db()
        self.assertEqual(exchange.status, ExchangeRequest.Status.PENDING)

    def test_receiver_can_accept_request_with_post(self):
        exchange = ExchangeRequest.objects.create(
            sender=self.alice_profile,
            receiver=self.bob_profile,
        )
        self.client.force_login(self.bob)
        url = reverse("accept_request", args=[exchange.pk])

        self.assertEqual(self.client.get(url).status_code, 405)
        self.client.post(url)

        exchange.refresh_from_db()
        self.assertEqual(exchange.status, ExchangeRequest.Status.ACCEPTED)

    def test_logout_requires_post(self):
        self.client.force_login(self.alice)

        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        response = self.client.post(reverse("logout"))

        self.assertRedirects(response, reverse("login"))
        self.assertNotIn("_auth_user_id", self.client.session)


@override_settings(SECURE_SSL_REDIRECT=False)
class StaffWorkflowTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username="staff",
            password="StrongPass123",
            is_staff=True,
        )
        self.member = User.objects.create_user(
            username="member",
            password="StrongPass123",
        )

    def test_staff_password_update_is_hashed(self):
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("edit_user", args=[self.member.pk]),
            {
                "username": "member",
                "first_name": "",
                "last_name": "",
                "email": "",
                "is_active": "on",
                "password": "UpdatedStrongPass456",
            },
        )

        self.assertRedirects(response, reverse("admin_dashboard"))
        self.member.refresh_from_db()
        self.assertTrue(self.member.check_password("UpdatedStrongPass456"))

    def test_user_deletion_requires_post(self):
        self.client.force_login(self.staff)
        url = reverse("delete_user", args=[self.member.pk])

        self.assertEqual(self.client.get(url).status_code, 405)
        self.client.post(url)

        self.assertFalse(User.objects.filter(pk=self.member.pk).exists())
