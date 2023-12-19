import random
import string

from django.core.mail import send_mail
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets, status
from rest_framework.generics import CreateAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from api.permissions import IsAdminUser, IsOwner
from api.serializers import (CategorySerializer,
                             GenreSerializer,
                             TitleSafeRequestSerializer,
                             TitleUnsafeRequestSerializer,
                             UserSignUpSerializer,
                             UserProfileSerializer,
                             CustomTokenObtainPairSerialiser,
                             UserSerializer)
from reviews.models import Category, CustomUser, Genre, Title


class CommentViewSet(viewsets.ModelViewSet):
    """
    Класс-обработчик API-запросов к комментариям к отзывам на произведения.
    """
    pass


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Класс-обработчик API-запросов к отзывам на произведения.
    """
    pass


class CategoryViewSet(viewsets.ModelViewSet):
    """
    Класс-обработчик API-запросов к категориям произведений.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(viewsets.ModelViewSet):
    """
    Класс-обработчик API-запросов к жанрам произведений.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """
    Класс-обработчик API-запросов произведениям.
    """
    queryset = Title.objects.all()
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', 'year', 'genre__slug', 'category__slug')

    def get_serializer_class(self):
        """
        Переопределение стандартного метода.
        В зависимости от метода запроса
        используется соответствующий сериализатор.
        """
        if self.request.method in permissions.SAFE_METHODS:
            return TitleSafeRequestSerializer
        return TitleUnsafeRequestSerializer


def generate_confirmation_code():
    confirmation_code_length = 6
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=confirmation_code_length))


class UserSignUpView(CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSignUpSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        confirmation_code = generate_confirmation_code()
        user.confirmation_code = confirmation_code
        user.save()

        send_mail(
            'Confirmation Code',
            f'Your confirmation code: {confirmation_code}',
            'from@example.com',
            [user.email],
            fail_silently=False,
        )
        return Response({'detail': 'Confirmation code sent'}, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomTokenObtainPairSerialiser
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        username = request.data.get('username')
        confirmation_code = request.data.get('confirmation_code')

        try:
            user = CustomUser.objects.get(username=username, confirmation_code=confirmation_code)
        except CustomUser.DoesNotExist:
            return Response({'error': ''}, status=404)

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        return JsonResponse({'token': access_token})


class UserProfileView(APIView):
    permission_classes = (IsAuthenticated, IsOwner)

    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)

    def patch(self, request):
        user = request.user
        serializer = UserProfileSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsAdminUser)
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    def perform_create(self, serializer):
        serializer.save()
