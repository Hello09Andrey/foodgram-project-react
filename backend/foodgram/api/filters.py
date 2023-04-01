from django_filters.rest_framework import FilterSet, filters
from recipes.models import Tags, Recipes, Ingredients

FILTER_DATA = {
    'favorites': 'favorites__user',
    'shop_card': 'shopping_cart__user'
}


class RecipeFilter(FilterSet):
    """Фильтр рецептов"""

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tags.objects.all(),
    )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipes
        fields = (
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def _get_queryset(self, queryset, name, value, data):
        if value:
            return queryset.filter(**{FILTER_DATA[data]: self.request.user})
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        return self._get_queryset(queryset, name, value, 'favorites')

    def filter_is_in_shopping_cart(self, queryset, name, value):
        return self._get_queryset(queryset, name, value, 'shop_card')


class IngredientFilter(FilterSet):
    """Поиск по названию ингредиента."""

    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredients
        fields = ('name',)
