from rest_framework import serializers
from django.db import transaction
from rest_framework.fields import SerializerMethodField, IntegerField
from drf_extra_fields.fields import Base64ImageField
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.db.models import F
from djoser.serializers import UserSerializer
from django.shortcuts import get_object_or_404
from users.models import CustomUser, Follow
from recipes.models import (
    Recipes,
    Tags,
    Ingredients,
    Favourites,
    ShoppingCart,
    IngredientsRecipe
)


class CustomUserSerializer(UserSerializer):
    """Cериализатор модели User"""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            tuple(CustomUser.REQUIRED_FIELDS) + (
                CustomUser.USERNAME_FIELD,
                'id',
                'is_subscribed',
            )
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user, author=obj
        ).exists()


class RecipeShortSerializer(serializers.ModelSerializer):
    """
    Вспомогательный сериализатор для FollowSerializer,
    FavoriteSerializer, ShoppingListSerializer
    """

    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FollowSerializer(CustomUserSerializer):
    """Сериализатор подпищиков"""

    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):

        fields = CustomUserSerializer.Meta.fields + (
            'recipes_count',
            'recipes'
        )
        read_only_fields = ('email', 'username')

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if user == author:
            raise ValidationError(
                detail='Вы не можете подписаться на самого себя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        serializer = RecipeShortSerializer(
            obj.recipes.all(),
            many=True,
            read_only=True
        )
        return serializer.data


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор модели Tag"""

    class Meta:
        fields = '__all__'
        model = Tags


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор модели Ingredients"""

    class Meta:
        fields = '__all__'
        model = Ingredients


class RecipesGetSerializer(serializers.ModelSerializer):
    """Сериализатор для получения рецептов"""

    tags = TagsSerializer(many=True, read_only=True)
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    ingredients = SerializerMethodField()

    class Meta:
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        model = Recipes

    def get_ingredients(self, obj):
        return obj.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('ingredientsrecipe__amount'),
        )

    def get_is_favorited(self, obj):
        return self._obj_exists(obj, Favourites)

    def get_is_in_shopping_cart(self, obj):
        return self._obj_exists(obj, ShoppingCart)

    def _obj_exists(self, recipe, name_class):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return name_class.objects.filter(
            user=request.user,
            recipes=recipe
        ).exists()


class AddIngredientInSerializer(serializers.ModelSerializer):
    """Вспомогательный сериализатор для RecipesCreateSerializer"""

    id = IntegerField(write_only=True)

    class Meta:
        model = IngredientsRecipe
        fields = ('id', 'amount')


class RecipesCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и изменения рецептов."""

    author = CustomUserSerializer(read_only=True)
    ingredients = AddIngredientInSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(),
        many=True,
    )
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate_tags(self, value):
        tags = value
        if not tags:
            raise ValidationError(
                {
                    'tags': 'Добавьте тег.'
                }
            )
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise ValidationError(
                    {
                        'tags': f'Тег {tag} существует!'
                    }
                )
            tags_list.append(tag)
        return value

    def validate_ingredients(self, value):
        ingredients = value
        if not ingredients:
            raise ValidationError({
                'ingredients': 'Нужен хотя бы один ингредиент!'
            })
        ingredients_list = []
        for item in ingredients:
            ingredient = get_object_or_404(Ingredients, id=item['id'])
            if ingredient in ingredients_list:
                raise ValidationError({
                    'ingredients': 'Ингридиенты не могут повторяться!'
                })
            if int(item['amount']) < 1:
                raise ValidationError({
                    'amount': 'Количество ингредиента должно быть больше 0!'
                })
            ingredients_list.append(ingredient)
        return value

    @transaction.atomic
    def add_ingredients(self, ingredients, recipe):
        IngredientsRecipe.objects.bulk_create(
            [IngredientsRecipe(
                ingredient=Ingredients.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipes.objects.create(
            author=self.context.get('request').user,
            **validated_data
        )
        recipe.tags.set(tags)
        self.add_ingredients(
            recipe=recipe,
            ingredients=ingredients
        )
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients_amounts(recipe=instance,
                                        ingredients=ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        return representation(self.context, instance, RecipesGetSerializer)
    # def to_representation(self, instance):
    #     request = self.context.get('request')
    #     context = {'request': request}
    #     return RecipesGetSerializer(instance,
    #                                 context=context).data


class FavoriteSerializer(RecipeShortSerializer):
    """Сериализатор для модели Favorite."""

    class Meta:
        model = Favourites
        fields = ('user', 'recipes')

    def to_representation(self, instance):
        return representation(
            self.context,
            instance.recipes,
            RecipeShortSerializer)


class ShoppingListSerializer(RecipeShortSerializer):
    """Сериализатор для модели ShoppingList."""

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipes')

    def to_representation(self, instance):
        return representation(
            self.context,
            instance.recipes,
            RecipeShortSerializer)


def representation(context, instance, serializer):
    """Функция для использования в to_representation"""

    request = context.get('request')
    new_context = {'request': request}
    return serializer(instance, context=new_context).data
