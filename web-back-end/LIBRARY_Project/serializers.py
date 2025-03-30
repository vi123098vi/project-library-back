from rest_framework import serializers


from .models import Book
class BookSerializers(serializers.ModelSerializer):
    class Meta:
        model=Book
        fields="__all__"

from .models import User
class UerSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields="__all__"

from .models import BorrowRecord
class BorrowRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model=BorrowRecord
        fields="__all__"




