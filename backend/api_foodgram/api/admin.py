from django.contrib import admin
from django.contrib.auth import get_user_model

from users.models import Follow

from .models import (Basket, Favorite, Ingredient, IngredientsForRecipe,
                     Recipe, Tag)

User = get_user_model()


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email')
    list_filter = ('username', 'email')
    empty_value_display = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    empty_value_display = '-пусто-'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class IngredientForRecipeAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'recipe', 'amount')
    empty_value_display = '-пусто-'


class IngredientInlineAdmin(admin.TabularInline):
    model = Recipe.ingredients.through
    fields = ('ingredient', 'amount',)


class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientInlineAdmin,)
    list_display = ('name', 'author')
    list_filter = ('name', 'author', 'tags')

    def amount_favorites(self, obj):
        return obj.favorites.count()


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


class BasketAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')


admin.site.register(User, UserAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientsForRecipe, IngredientForRecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Basket, BasketAdmin)
admin.site.register(Follow, FollowAdmin)
