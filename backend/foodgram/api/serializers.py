import webcolors
from django.db.models import F
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag
)
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from users.models import Subscription, User


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError("Для этого цвета нет имени")
        return data


class CreateUserSerializer(UserCreateSerializer):
    """Сериализатор для регистрации пользователей."""

    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
        )
        extra_kwargs = {"password": {"write_only": True}}


class UsersSerializer(UserSerializer):
    """Сериализатор пользователей."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        if user.is_authenticated:
            return Subscription.objects.filter(user=user, author=obj).exists()
        return False


class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = "__all__"


class IngredientCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиентов при создании рецепта."""

    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ("id", "amount")


class ReadIngredientsInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения ингредиентов в рецепте."""

    id = serializers.ReadOnlyField(source="ingredients.id")
    name = serializers.ReadOnlyField(source="ingredients.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredients.measurement_unit"
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""

    author = UsersSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get("request").user
        if user.is_authenticated:
            return ShoppingCart.objects.filter(user=user, recipe=obj).exists()
        return False

    def get_is_favorited(self, obj):
        user = self.context.get("request").user
        if user.is_authenticated or self.context.get("request") is not None:
            return Favorite.objects.filter(user=user, recipe=obj).exists()
        return False

    @staticmethod
    def get_ingredients(obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return ReadIngredientsInRecipeSerializer(ingredients, many=True).data


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецептов."""

    ingredients = IngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    name = serializers.CharField(max_length=200)
    cooking_time = serializers.IntegerField()
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
            "author",
        )

    @staticmethod
    def create_ingredients(ingredients, recipe):
        for ingredient in ingredients:
            amount = ingredient["amount"]
            if RecipeIngredient.objects.filter(
                recipe=recipe,
                ingredients=get_object_or_404(Ingredient, id=ingredient["id"]),
            ).exists():
                amount += F("amount")
            RecipeIngredient.objects.update_or_create(
                recipe=recipe,
                ingredients=get_object_or_404(Ingredient, id=ingredient["id"]),
                defaults={"amount": amount},
            )

    def create(self, validated_data):
        tags_data = validated_data.pop("tags")
        ingredients_data = validated_data.pop("ingredients")
        image = validated_data.pop("image")
        recipe = Recipe.objects.create(image=image, **validated_data)
        self.create_ingredients(ingredients_data, recipe)
        recipe.tags.set(tags_data)
        return recipe

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        self.create_ingredients(ingredients, recipe)
        recipe.tags.set(tags)
        return super().update(recipe, validated_data)

    def to_representation(self, recipe):
        data = RecipeSerializer(
            recipe, context={"request": self.context.get("request")}
        ).data
        return data


class RecipeForFollowersSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода рецептов в избранном и списке покупок."""

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class RecipeSubscriptionUserField(serializers.Field):
    """Сериализатор для вывода рецептов в подписках."""

    def get_attribute(self, instance):
        return Recipe.objects.filter(author=instance.author)

    def to_representation(self, recipes_list):
        recipes_data = []
        for recipes in recipes_list:
            recipes_data.append(
                {
                    "id": recipes.id,
                    "name": recipes.name,
                    "image": recipes.image.url,
                    "cooking_time": recipes.cooking_time,
                }
            )
        return recipes_data


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""

    recipes = RecipeSubscriptionUserField()
    recipes_count = serializers.SerializerMethodField(read_only=True)
    id = serializers.ReadOnlyField(source="author.id")
    email = serializers.ReadOnlyField(source="author.email")
    username = serializers.ReadOnlyField(source="author.username")
    first_name = serializers.ReadOnlyField(source="author.first_name")
    last_name = serializers.ReadOnlyField(source="author.last_name")
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(
            author=obj.author
        ).count()

    def get_is_subscribed(self, obj):
        return Subscription.objects.filter(
            user=obj.user, author=obj.author
        ).exists()
