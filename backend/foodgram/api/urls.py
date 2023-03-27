from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    CustomUserViewSet,
    TagViewSet,
    IngredientsViewSet,
    RecipesViewSet
)


router_v1 = DefaultRouter()
router_v1.register('users', CustomUserViewSet)
router_v1.register('tags', TagViewSet)
router_v1.register('ingredients', IngredientsViewSet)
router_v1.register('recipes', RecipesViewSet)

urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
