from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Model
from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST)
from users.serializers import FollowRecipeSerializer

from .models import Basket, Favorite, Recipe

ANSWERS = {
    Favorite: ['избранное', 'избранном'],
    Basket: ['корзину', 'корзине']
}


def recipe_is_exist(recipe_id):
    try:
        recipe = get_object_or_404(Recipe, id=recipe_id)
        return recipe
    except ObjectDoesNotExist:
        raise Response(
            data={'errors': 'Такого рецепта не существует'},
            status=HTTP_400_BAD_REQUEST)


def add_to(model: Model, user, pk):
    recipe = recipe_is_exist(pk)
    obj, obj_status = model.objects.get_or_create(user=user, recipe=recipe)
    if obj_status:
        serializer = FollowRecipeSerializer(recipe)
        return Response(serializer.data, status=HTTP_201_CREATED)

    return Response(
        data={'errors': f'Рецепт уже добавлен в {ANSWERS[model][0]}'},
        status=HTTP_400_BAD_REQUEST)


def delete_from(model, user, pk):
    recipe = recipe_is_exist(pk)
    obj = model.objects.filter(user=user, recipe=recipe)
    if obj.exists():
        obj.delete()
        return Response(status=HTTP_204_NO_CONTENT)
    return Response(
        data={'errors': f'Рецепта нет в {ANSWERS[model][1]}'},
        status=HTTP_400_BAD_REQUEST)
