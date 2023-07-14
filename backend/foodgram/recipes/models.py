from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models.constraints import UniqueConstraint

from users.models import User

MIN_VALUE = 1


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Название тэга",
        help_text="Введите название тэга",
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name="Цвет",
        help_text="Выберите цвет",
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[-a-zA-Z0-9_]+$",
            )
        ],
        help_text="Укажите слаг",
    )

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название",
        help_text="Введите название ингредиента",
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name="Мера измерения",
        help_text="Введите единицу измерения",
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Пользователь (В рецепте - автор рецепта)",
        help_text="Автор рецепта",
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Название",
        help_text="Название рецепта",
    )
    image = models.ImageField(
        verbose_name="Ссылка на картинку на сайте",
        upload_to="recipes/",
        blank=True,
        help_text="Добавьте изображение рецепта",
    )
    text = models.TextField(
        verbose_name="Описание", help_text="Описание приготовление рецепта"
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        verbose_name="Список ингредиентов",
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Теги",
        help_text="Выберите тэг",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Дата публикации",
        help_text="Дата публикации",
    )
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(MIN_VALUE, message="Минимум 1")],
        verbose_name="Время приготовления (в минутах)",
        help_text="Укажите время приготовления в минутах",
    )

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        help_text="Выберите рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиент",
        help_text="Укажите ингредиенты",
    )
    amount = models.IntegerField(
        validators=[MinValueValidator(MIN_VALUE, "Минимум 1 ингредиент")],
        verbose_name="Количество ингредиентов",
        help_text="Укажите количество ингредиента",
    )

    class Meta:
        default_related_name = "recipeingredients"
        verbose_name = "Ингредиент для рецепта"
        verbose_name_plural = "Ингредиенты для рецепта"


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        help_text="Выберите рецепт",
    )

    class Meta:
        default_related_name = "favorites"
        ordering = ["-id"]
        constraints = [
            UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_subscription",
            )
        ]
        verbose_name = "Рецепт в избранном"
        verbose_name_plural = "Рецепты в избранном"

    def __str__(self):
        return f"{self.recipe.name} теперь у {self.user.username} в избраннном"


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="carts",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        help_text="Выберите рецепт",
    )

    class Meta:
        default_related_name = "carts"
        ordering = ["-id"]
        constraints = [
            UniqueConstraint(
                fields=["user", "recipe"], name="unique_user_shopping_cart"
            )
        ]
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"

    def __str__(self):
        return f"{self.recipe.name} у {self.user.username} в списке покупок"
