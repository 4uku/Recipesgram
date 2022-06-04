from functools import reduce

from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .models import (Basket, Favorite, Ingredient, IngredientsForRecipe,
                     Recipe, Tag)
from .permissions import AnonOrAuthOrAuthor
from .serializers import (IngredientViewSetSerializer,
                          RecipesViewSetInputSerializer,
                          RecipesViewSetOutputSerializer, TagViewSetSerializer)
from .utils import add_to, delete_from


class TagViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagViewSetSerializer
    pagination_class = None


class IngredientViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientViewSetSerializer
    filter_class = IngredientFilter
    pagination_class = None
    search_fields = ['^name']


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (AnonOrAuthOrAuthor,)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return RecipesViewSetOutputSerializer
        return RecipesViewSetInputSerializer

    def create_ingredients_for_recipe(self, ingredients, recipe):
        list_of_ingredients = [
            IngredientsForRecipe(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']) for ingredient in ingredients]
        IngredientsForRecipe.objects.bulk_create(list_of_ingredients)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        tags = serializer.initial_data['tags']
        serializer.validated_data.pop('tags')
        image = serializer.validated_data.pop('image')
        ingredients = serializer.validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            image=image, author=request.user,
            **serializer.validated_data)
        recipe.tags.set(tags)
        self.create_ingredients_for_recipe(ingredients, recipe)
        response = RecipesViewSetOutputSerializer(recipe)
        return Response(response.data)

    def update(self, request, pk, *args, **kwargs):
        recipe = self.queryset.get(id=pk)
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        tags = serializer.initial_data['tags']
        serializer.validated_data.pop('tags')
        recipe.image = serializer.validated_data.get('image', recipe.image)
        recipe.name = serializer.validated_data.get('name', recipe.name)
        recipe.text = serializer.validated_data.get('text', recipe.text)
        recipe.cooking_time = serializer.validated_data.get(
            'cooking_time', recipe.cooking_time)
        recipe.tags.clear()
        recipe.tags.set(tags)
        IngredientsForRecipe.objects.filter(recipe=recipe).all().delete()
        self.create_ingredients_for_recipe(
            serializer.validated_data.get('ingredients'), recipe)
        recipe.save()
        response = RecipesViewSetOutputSerializer(recipe)
        return Response(response.data)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        if request.method == 'POST':
            return add_to(Favorite, request.user, pk)
        return delete_from(Favorite, request.user, pk)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return add_to(Basket, request.user, pk)
        return delete_from(Basket, request.user, pk)

    @action(detail=False, methods=['GET'],
            permission_classes=[IsAuthenticated],)
    def download_shopping_cart(self, request):
        text = 'Ваш список покупок:\n\n'
        user = request.user
        ingredients = Recipe.objects.filter(
            basket__user=user
        ).values('ingredients__name',
                 'ingredients__measurement_unit').annotate(
                     amount=Sum('ingredients_for_recipe__amount'))

        ingredients_list = {}
        for ingredient in ingredients:
            key = (f'{ingredient["ingredients__name"]}, '
                   f'{ingredient["ingredients__measurement_unit"]}')
            if key in ingredients_list:
                ingredients_list[key] += ingredient['amount']
            else:
                ingredients_list[key] = ingredient['amount']

        text += reduce(
            lambda x, key:
            x + '   ' + key + ' -- ' + str(ingredients_list[key]) + '\n',
            ingredients_list, '')

        response = HttpResponse(text, content_type='text/plain; charset=utf-8')
        filename = 'shopping_list.txt'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
