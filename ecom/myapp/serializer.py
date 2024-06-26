# serializers.py
from rest_framework import serializers
from .models import Category, SubCategory, Brand, Product,PurchaseHistory

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = '__all__'

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'

# class ProductSerializer(serializers.ModelSerializer):
#     brand = BrandSerializer()
#     category = CategorySerializer()
#     sub_category = SubCategorySerializer()

#     class Meta:
#         model = Product
#         fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class PurchaseHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseHistory
        fields = '__all__'
        
        
from rest_framework import serializers
from .models import Product

class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
