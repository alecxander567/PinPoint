from rest_framework import serializers
from .models import User
import bcrypt


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "name", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        # hash password
        password = validated_data.pop("password")
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        validated_data["password"] = hashed.decode("utf-8")
        return User.objects.create(**validated_data)
