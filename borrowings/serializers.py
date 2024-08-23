from datetime import date

from rest_framework import serializers

from borrowings.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ["id", "user", "book", "borrow_date", "expected_return_date", "actual_return_date"]
        read_only_fields = ["borrow_date", "user"]

    def create(self, validated_data):
        book = validated_data["book"]
        book.borrow()
        return super().create(validated_data)


class BorrowingReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ["actual_return_date"]

    def validate(self, data):
        if self.instance.actual_return_date is not None:
            raise serializers.ValidationError("This book has already been returned.")
        return data

    def update(self, instance, validated_data):
        instance.actual_return_date = validated_data.get("actual_return_date", date.today())
        instance.book.return_book()
        instance.save()
        return instance
