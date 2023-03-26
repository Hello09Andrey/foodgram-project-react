from django.contrib import admin
from .models import (
    Tags,
    Ingredients,
    Recipes,
    IngredientsRecipe,
    Favourites,
    ShoppingCart
)
from django.contrib.admin import display


class RecipesAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'favorites',
    )
    list_filter = (
        'author',
        'name',
        'tags',
    )
    filter_horizontal = ('tags',)
    readonly_fields = ('favorites',)

    @display(description='Количество в избранных')
    def favorites(self, obj):
        return obj.favorites.count()


class IngredientsAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    list_filter = ('name',)


admin.site.register(Tags)
admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(Recipes, RecipesAdmin)
admin.site.register(IngredientsRecipe)
admin.site.register(Favourites)
admin.site.register(ShoppingCart)
