from rest_framework import serializers

from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "id",
            "user",
            "bio",
            "avatar",
            "location",
            "birth_date",
            "created_at",
            "updated_at",
        ]
        read_only = ["user", "created_at", "updated_at"]
