from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST,
                                   HTTP_401_UNAUTHORIZED)

from .models import Follow
from .serializers import (FollowUserSerializer, GetTokenSerializer,
                          UserSetPasswordSerializer,
                          UserViewSetInputSerializer,
                          UserViewSetOutputSerializer)

User = get_user_model()


@api_view(['POST'])
def get_token(request):
    serializer = GetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data.get('email')
    user = get_object_or_404(User, email=email)
    token = Token.objects.create(user=user)
    return Response(
        {'auth_token': f'{token.key}'}, status=HTTP_201_CREATED
    )


@api_view(['POST'])
def delete_token(request):
    if not request.user.is_authenticated:
        return Response(
            {'detail': 'Вы не авторизованы'}, status=HTTP_401_UNAUTHORIZED
        )
    token = get_object_or_404(Token, user=request.user)
    token.delete()
    return Response(status=HTTP_204_NO_CONTENT)


class UserViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    pagination_class = LimitOffsetPagination

    action_serializer_classes = {
        'create': UserViewSetInputSerializer,
        'list': UserViewSetOutputSerializer,
        'retrieve': UserViewSetOutputSerializer
    }

    def retrieve(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return Response(
                data={
                    'detail': 'Учетные данные не были предоставлены'
                },
                status=HTTP_401_UNAUTHORIZED
            )
        return super().retrieve(request, *args, **kwargs)

    def get_serializer_class(self):
        return self.action_serializer_classes.get(self.action, None)

    def create(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer_data = serializer_class(data=request.data)
        serializer_data.is_valid(raise_exception=True)
        password = serializer_data.validated_data.get('password')
        hash_password = make_password(password)
        serializer_data.validated_data['password'] = hash_password
        user = User.objects.create(**serializer_data.validated_data)
        response = serializer_class(user)
        return Response(response.data)

    @action(methods=['POST'], detail=False,
            permission_classes=[IsAuthenticated])
    def set_password(self, request):
        serializer = UserSetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_password = serializer.validated_data.get('new_password')
        current_password = serializer.validated_data.get('current_password')
        user = get_object_or_404(User, id=request.user.id)
        if not check_password(current_password, user.password):
            return Response({'current_password': 'Текущий пароль неверен'},
                            status=HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(methods=['GET'], detail=False,
            permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = UserViewSetOutputSerializer(request.user)
        return Response(serializer.data, status=HTTP_200_OK)

    @action(methods=['GET'], detail=False,
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        follows = Follow.objects.filter(user=request.user)
        pages = self.paginate_queryset(follows)
        serializer = FollowUserSerializer(
            pages, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk):
        answers = {
            'POST': ['Подписаться', 'на'],
            'DELETE': ['Отписаться', 'от']
        }

        if pk == request.user.pk:
            return Response(
                data={'errors': f'Вы не можете {answers[request.method][0]} '
                                f'{answers[request.method][1]} самого себя'},
                status=HTTP_400_BAD_REQUEST)

        author = get_object_or_404(User, id=pk)

        if request.method == 'DELETE':
            try:
                follow = Follow.objects.get(user=request.user, author=author)
                follow.delete()
                return Response(status=HTTP_204_NO_CONTENT)
            except ObjectDoesNotExist:
                return Response(
                    data={'errors': 'Вы не подписаны на данного автора'},
                    status=HTTP_400_BAD_REQUEST)

        if request.method == 'POST':
            if Follow.objects.filter(
                    user=request.user, author=author).exists():
                return Response(
                    data={'errors': 'Вы уже подписаны на данного автора'},
                    status=HTTP_400_BAD_REQUEST)
            follow = Follow.objects.create(user=request.user, author=author)
            response = FollowUserSerializer(follow)
            return Response(response.data, status=HTTP_201_CREATED)
