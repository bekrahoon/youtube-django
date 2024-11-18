from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from user_profile_app.models import UserProfile
from user_profile_app.serializers import UserProfileSerializer
from user_profile_app.permissions import IsOwnerOrReadOnly


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    Представление для работы с профилем пользователя:
    - Получение профиля
    - Обновление профиля
    - Удаление профиля
    """

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        # Создание профиля пользователя
        serializer.save(user=self.request.user)

    def get_queryset(self):
        # Получение только профиля текущего пользователя
        return UserProfile.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        """
        Обновление информации профиля. Поддерживает PATCH и PUT запросы.
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()  # Получаем текущий профиль пользователя
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Удаление профиля текущего пользователя.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
