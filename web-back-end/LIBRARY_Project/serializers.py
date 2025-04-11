
from .models import User
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            'email': {'required': False},
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        user=User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
        )
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        # 其他字段正常更新
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


from .models import Book
class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model=Book
        fields="__all__"

class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model=Book
        fields = '__all__'

from .models import BorrowRecord
class BorrowRecordSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)
    class Meta:
        model=BorrowRecord
        fields="__all__"

from .models import ReviewLog
class ReviewLogSerializer(serializers.ModelSerializer):
    class Meta:
        model=ReviewLog
        fields="__all__"





