from django.db import models
from django.db.models import UniqueConstraint
from django.core.validators import MinValueValidator

from users.models import CustomUser
from django.conf import settings


class Tags(models.Model):
    """Модель списка тегов"""

    name = models.CharField('Название', max_length=150, unique=True)
    color = models.CharField('Цвет', max_length=7, unique=True)
    slug = models.SlugField('Слаг', unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'{self.name}'


class Ingredients(models.Model):
    """Модель ингредиентов"""

    name = models.CharField('Название ингредиента', max_length=150)
    measurement_unit = models.CharField('Единицы измерения', max_length=25)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipes(models.Model):
    """Модель рецептов"""

    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        verbose_name='Ингредиенты',
        related_name='recipes',
        through='IngredientsRecipe'
    )
    tags = models.ManyToManyField(
        Tags,
        related_name='recipes',
        verbose_name='Теги',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='movies',
        blank=True,
        help_text='Картинка'
    )
    name = models.CharField('Название', max_length=200)
    text = models.TextField('Описание')
    cooking_time = models.PositiveBigIntegerField(
        'Время приготовления',
        validators=(
            MinValueValidator(
                limit_value=1,
                message=(
                    'Время приготовления не может быть менее одной минуты.'
                ),
            ),
        )
    )
    pub_date = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return self.name[:settings.LEN_NAME_IN_STR]


class IngredientsRecipe(models.Model):
    """Модель ингредиентов рецепта"""

    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_ingredient'
    )
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=(
            MinValueValidator(
                limit_value=0.01,
                message='Значение должно быть больше нуля',
            ),
        )
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique ingredient for recipe',
            )
        ]

    def __str__(self):
        return (f'{self.recipe}: {self.ingredient.name},'
                f' {self.amount}, {self.ingredient.measurement_unit}')


class Favourites(models.Model):
    """Модель избранного"""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Избранное Автора',
    )
    recipes = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='Избраный рецепт',
        related_name='favorites',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipes'],
                name='unique_favourite'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил "{self.recipes}" в Избранное'


class ShoppingCart(models.Model):
    """Модель списка покупок"""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipes = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзина покупок'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipes'],
                name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил "{self.recipes}" в Корзину покупок'
