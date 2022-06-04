from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, RecipesViewSet, TagViewSet

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tagviweset')
router.register('ingredients', IngredientViewSet, basename='ingredientviewset')
router.register('recipes', RecipesViewSet, basename='recipeviewset')

urlpatterns = [
    path('users/', include('users.urls')),
    path('auth/', include('users.urls')),
    path('', include(router.urls))
]
