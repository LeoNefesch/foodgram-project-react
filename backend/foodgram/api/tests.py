from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient


class FoodAPITestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="auth_user")
        self.guest_client = APIClient()
        self.authenticated_client = APIClient()
        self.authenticated_client.force_authenticate(user=self.user)

    def test_users_list_exists(self):
        """Проверка доступности списка пользователей."""
        response = self.guest_client.get("/api/users/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_tags_list_exists(self):
        """Проверка доступности списка тэгов."""
        response = self.guest_client.get("/api/tags/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_recipes_list_exists(self):
        """Проверка доступности списка рецептов."""
        response = self.guest_client.get("/api/recipes/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_shopping_cart_exists(self):
        """Проверка доступности скачанной карты покупок."""
        response = self.authenticated_client.get(
            "/api/recipes/download_shopping_cart/"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_favorite_list_exists(self, recipe):
        """Проверка доступности списка избранных рецептов."""
        response = self.authenticated_client.get(
            "/api/recipes/{recipe.id}/favorite/"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_ingredients_list_exists(self):
        """Проверка доступности списка рецептов."""
        response = self.guest_client.get("/api/ingredients/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_subscriptions_for_authenticateds(self):
        """Проверка доступности подписок для авторизованных пользователей."""
        response = self.authenticated_client.get("/api/users/subscriptions/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_subscriptions_for_guests(self):
        """Проверка доступности подписок для гостей сайта."""
        response = self.guest_client.get("/api/users/subscriptions/")
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_subscribe_for_authenticateds(self, user):
        """Проверка возможности подписаться авторизованному пользователю."""
        response = self.authenticated_client.get(
            "/api/users/{user.id}/subscribe/"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_subscribe_for_guests(self):
        """Проверка доступности списка рецептов."""
        response = self.guest_client.get("/api/users/{user.id}/subscribe/")
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
