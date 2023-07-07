from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import F, Q
from django.db.models.constraints import CheckConstraint, UniqueConstraint


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        null=False,
        verbose_name="Логин",
        validators=[
            RegexValidator(
                regex=r"^[-a-zA-Z0-9_]+$",
            )
        ],
        help_text="Введите логин",
    )
    password = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        verbose_name="Пароль",
        help_text="Введите пароль",
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
        null=False,
        verbose_name="Email",
        help_text="Введите email",
    )
    first_name = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        verbose_name="Имя",
        help_text="Ваше имя",
    )
    last_name = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        verbose_name="Фамилия",
        help_text="Ваша фамилия",
    )

    class Meta:
        ordering = ("id",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Пользователь",
        help_text="Текущий пользователь",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Автор",
        help_text="Подписаться на автора рецепта(ов)",
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["user", "author"],
                name="unique_user_author"
            ),
            CheckConstraint(
                check=~Q(user=F("author")),
                name="no_self_following"
            ),
        ]
        ordering = ["-id"]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return f"{self.user.username} подписан на {self.author.username}"
