from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404

from api.models import Recipe
from rest_framework import serializers

from .models import Follow

User = get_user_model()

BAD_USERNAME = [
    'me',
    'token',
]


class UserViewSetInputSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(max_length=254)
    username = serializers.CharField(
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z', message='Введены некорректные символы')
        ]
    )
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=150, write_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password')
        required_fields = ('email', 'username', 'first_name', 'last_name',
                           'password')

    def validate_username(self, value):
        if value in BAD_USERNAME:
            raise serializers.ValidationError('Недопустимый username')
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                'Пользователь с таким username уже зарегистриован')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'Пользовател с таким email уже зарегистрирован')
        return value


class UserViewSetOutputSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Follow.objects.filter(user=request.user, author=obj).exists()


class FollowRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowUserSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(
        source='author.recipes.count')

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.author.recipes.all()
        if request:
            recipes_limit = request.GET.get('recipes_limit')
            if recipes_limit:
                recipes = recipes[:int(recipes_limit)]
        return FollowRecipeSerializer(recipes, many=True).data

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user, author=obj.author
        ).exists()


class UserSetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, max_length=150)
    current_password = serializers.CharField(required=True, max_length=150)


class GetTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, max_length=254)
    password = serializers.CharField(required=True, max_length=150)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'Пользователь с таким email не найден')
        return value

    def validate(self, data):
        email = data.get('email')
        user = get_object_or_404(User, email=email)
        if not user.check_password(data.get('password')):
            raise serializers.ValidationError(
                detail={'error': 'Комбинация email и password не совпадает'})
        return data
