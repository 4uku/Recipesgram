from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from users.serializers import UserViewSetOutputSerializer

from .models import (Basket, Favorite, Ingredient, IngredientsForRecipe,
                     Recipe, Tag)


class IngredientViewSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientsForRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientsForRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AddIngredientForRecipeSerialzier(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientsForRecipe
        fields = ('id', 'amount')

    def validate(self, data):
        if data['amount'] < 1:
            raise serializers.ValidationError(
                f'Количество ингредиента {data["id"]} должно быть больше '
                'либо равно 1'
            )
        return data


class TagViewSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipesViewSetInputSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    image = Base64ImageField(required=True)
    ingredients = AddIngredientForRecipeSerialzier(many=True)
    name = serializers.CharField(required=True, max_length=200)
    text = serializers.CharField(required=True)
    cooking_time = serializers.IntegerField(required=True, min_value=1)

    class Meta:
        model = Recipe
        read_only_fields = ('author',)
        fields = ('tags', 'author', 'ingredients', 'name', 'text',
                  'image', 'cooking_time',)

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError('Ни один ингредиент не выбран')
        ingredient_list = []
        for ingredient_item in value:
            if ingredient_item['id'] in ingredient_list:
                raise serializers.ValidationError(
                    'Ингредиенты должны быть уникальными')
            ingredient_list.append(ingredient_item['id'])
        return value

    def validate_tags(self, value):
        if len(set(value)) != len(value):
            raise serializers.ValidationError(
                'Теги должны быть уникальными'
            )
        return value


class RecipesViewSetOutputSerializer(serializers.ModelSerializer):
    author = UserViewSetOutputSerializer(read_only=True)
    tags = TagViewSetSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'text',
                  'image', 'cooking_time', 'is_favorited',
                  'is_in_shopping_cart')

    def get_ingredients(self, obj):
        ingredients = obj.ingredients_for_recipe.all()
        return IngredientsForRecipeSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Basket.objects.filter(user=request.user, recipe=obj).exists()


class AddFavoriteBasketSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')
