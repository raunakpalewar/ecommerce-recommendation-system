from myapp.ecom7 import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import *
from django.contrib.auth.hashers import make_password, check_password
import re
from django.contrib.auth import login, logout
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from datetime import timedelta
from .serializer import *
from myapp.pagination import CustomPageNumberPagination
from django.utils import timezone
from myapp.python_script import *
from django.db.models import Min, Max, Avg
from django.db.models import F


class CustomerRegistration(APIView):
    @swagger_auto_schema(
        operation_description="This if for Customer Registration",
        operation_summary="Customer can Register using this api",
        tags=['OAuth'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
                'address': openapi.Schema(type=openapi.TYPE_STRING),
                
            },
            requried=['email', 'password', 'name',
                       'address']
        ),
    )
    def post(self, request):
        try:
            data = request.data
            try:
                email = data.get('email')
                password = data.get('password')
                name = data.get('name')
                address = data.get('address')

                def password_validate(password):
                    if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*(){}[\]:;,<>\'\"~])[A-Za-z\d!@#$%^&*(){}[\]:;,<>\'\"~]{8,16}$', password):
                        raise ValueError(
                            "Password must be 8 to 16 characters long with one uppercase, one lowercase, a number, and a special character.")
                email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

                if not email or not re.match(email_regex, email):
                    return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': "Invalid email format"}, status=status.HTTP_400_BAD_REQUEST)
                if not password:
                    return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': "Password is required."}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    password_validate(password)
                except Exception as e:
                    return Response({'status': status.HTTP_500_INTERNAL_SERVER_ERROR, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                otp = generate_otp()
                print(otp)
                send_otp_email(email, otp)
                user_password = make_password(password)
                user = UserRegistration.objects.create(email=email, password=user_password,
                                                       otp=otp, full_name=name, address=address)
                user.otp_created_at = timezone.now()
                user.user_created_at = timezone.now()
                user.is_registered = True
                user.save()
                return Response({'message': 'user registered successfully'}, status=status.HTTP_201_CREATED)
            except Exception as e:
                print(str(e))
                return Response({"status": status.HTTP_400_BAD_REQUEST, 'message': 'could not register user try again'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(str(e))
            return Response({"status": status.HTTP_500_INTERNAL_SERVER_ERROR, 'message': 'could not register user try again'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyEmail(APIView):
    @swagger_auto_schema(
        operation_description='Verify you email',
        operation_summary='user has to verify his/her email using the otp sended within 3 minutes',
        tags=['OAuth'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'otp': openapi.Schema(type=openapi.TYPE_NUMBER)
            },
        ),
    )
    def post(self, request):
        data = request.data
        email = data.get('email')
        otp = data.get('otp')

        try:
            user = UserRegistration.objects.get(email=email)
            time_difference = timezone.now()-user.otp_created_at
            if time_difference <= timedelta(minutes=3):
                if int(otp) == int(user.otp):
                    user.is_valid = True
                    user.is_verified = True
                    user.save()
                    return Response({'status': status.HTTP_200_OK, 'message': "User Verified Successfully"}, status=status.HTTP_200_OK)
                return Response({'status': status.HTTP_400_BAD_REQUEST, "message": "Invalid OTP"}, status.HTTP_400_BAD_REQUEST)
            else:
                otp = generate_otp()
                send_otp_email(email, otp)
                user.otp = otp
                user.otp_created_at = timezone.now()
                user.save()
                return Response({'status': status.HTTP_400_BAD_REQUEST, "message": "time out for  OTP \n new opt sended \n try again using new otp"}, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(str(e))
            return Response({'status': status.HTTP_404_NOT_FOUND, "message": "User not found"}, status.HTTP_404_NOT_FOUND)


class Login(APIView):
    @swagger_auto_schema(
        operation_description="login here",
        operation_summary='login to you account',
        tags=['OAuth'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
    )
    def post(self, request):
        try:
            data = request.data

            email = data.get('email')
            password = data.get('password')

            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not email or not re.match(email_regex, email):
                return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': "Invalid email format"}, status=status.HTTP_400_BAD_REQUEST)
            if not password:
                return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': "Password is required."}, status=status.HTTP_400_BAD_REQUEST)

            user = UserRegistration.objects.get(
                email=email, is_verified=True, is_registered=True)

            try:
                if check_password(password, user.password):
                    try:
                        login(request, user)
                        token = get_token_for_user(user)
                        # serializer=UserRegistrationsSerializer(user)
                        return Response({"status": status.HTTP_200_OK, 'message': 'Login successfully', 'token': token, "Your user id": user.id}, status=status.HTTP_200_OK)
                    except Exception as e:
                        print(str(e))
                        return Response({"messsage": f"user not verified please verify you email first using otp {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    print(str(e))
                    return Response({"status": status.HTTP_400_BAD_REQUEST, 'message': "invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                print(str(e))
                return Response({"status": status.HTTP_400_BAD_REQUEST, 'message': 'user not found', "error_message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(str(e))
            return Response({"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserLogout(APIView):
    def get(self, request):
        logout(request)
        return Response({"status": status.HTTP_200_OK, 'message': 'logout successfully done'}, status.HTTP_200_OK)


class ForgotPassword(APIView):
    @swagger_auto_schema(
        operation_description="Forgot Password",
        operation_summary="Reset Your password using new otp",
        tags=['OAuth'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING)
            },
        ),
    )
    def post(self, request):
        try:
            data = request.data
            email = data.get('email')
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not email:
                return Response({'message': 'Email id is required.'}, status=status.HTTP_400_BAD_REQUEST)
            if not re.match(email_regex, email):
                return Response({'message': 'Please enter a valid email address.'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                user = UserRegistration.objects.get(email=email)
                otp = generate_otp()
                send_otp_email(email, otp)
                user.otp = otp
                user.otp_created_at = timezone.now()
                user.save()
                return Response({'message': 'OTP sent successfully for password reset.'}, status=status.HTTP_200_OK)

            except UserRegistration.DoesNotExist:
                return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        except UserRegistration.DoesNotExist:
            return Response({'message': 'User not found.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SetNewPassword(APIView):
    @swagger_auto_schema(
        operation_description='Set New Password',
        operation_summary='Please Enter you new password',
        tags=['OAuth'],

        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'otp': openapi.Schema(type=openapi.TYPE_NUMBER),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING),
                'confirm_password': openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
    )
    def post(self, request):
        try:
            data = request.data
            email = data.get('email')
            # data['email'] = email

            otp = data.get('otp')
            password = data.get('new_password')
            cpassword = data.get('confirm_password')

            if not password:
                return Response({"message": "Please enter a new password"}, status=status.HTTP_400_BAD_REQUEST)
            if password != cpassword:
                return Response({"message": "New password and Confirm password must be the same."}, status=status.HTTP_400_BAD_REQUEST)

            password_regex = r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$'
            if not re.match(password_regex, password):
                return Response({"message": "Invalid password format"}, status=status.HTTP_403_FORBIDDEN)

            try:
                user = UserRegistration.objects.get(email=email)
                time_difference = timezone.now()-user.otp_created_at
                if time_difference <= timedelta(minutes=3):
                    if otp == user.otp:
                        user.set_password(password)
                        user.save()
                        return Response({'status': status.HTTP_200_OK, 'message': "Password Changed Successfully"}, status=status.HTTP_200_OK)
                    return Response({'status': status.HTTP_400_BAD_REQUEST, "message": "Invalid OTP"}, status.HTTP_400_BAD_REQUEST)
                else:
                    otp = generate_otp()
                    send_otp_email(email, otp)
                    user.otp = otp
                    user.otp_created_at = timezone.now()
                    user.save()
                    return Response({'status': status.HTTP_400_BAD_REQUEST, "message": "time out for  OTP \n new opt sended \n try again using new otp"}, status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'status': status.HTTP_404_NOT_FOUND, "message": f"User not found {str(e)}"}, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'status': status.HTTP_500_INTERNAL_SERVER_ERROR, "message": f"User not found{str(e)}"}, status.HTTP_500_INTERNAL_SERVER_ERROR)




class get_all_products(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    serializer_class = ProductSerializer
    swagger_auto_schema(
        operation_description="Get all Products",
        operation_summary="Retrieve all existing Products",
        tags=['Food'],
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER,
                              type=openapi.TYPE_STRING)
        ],
        responses={
            status.HTTP_200_OK: "List of all Products",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal server error",
        }
    )
    def get(self, request):
        try :
            queryset = Product.objects.all()

            # Paginate the queryset
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(queryset, request)

            # Serialize the paginated queryset
            serializer = self.serializer_class(paginated_queryset, many=True)

            # Return the paginated response
            response= paginator.get_paginated_response(serializer.data)
            return Response({"response":response.data,"status":status.HTTP_200_OK},status.HTTP_200_OK)
        except Exception as e:
            return({"response":f"{str(e)}","status":status.HTTP_400_BAD_REQUEST},status.HTTP_400_BAD_REQUEST)



class AllBrands(APIView):
    def get(self, request):
        try:
            brands = Brand.objects.values_list('name', flat=True).distinct()
            return Response({"brands": list(brands)}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"response": f"{str(e)}", "status": status.HTTP_500_INTERNAL_SERVER_ERROR}, status.HTTP_500_INTERNAL_SERVER_ERROR)

        

class AllSubcategories(APIView):
    def get(self, request):
        try:
            subcategories = SubCategory.objects.values_list('name', flat=True).distinct()
            return Response({"subcategories": list(subcategories)}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"response": f"{str(e)}", "status": status.HTTP_500_INTERNAL_SERVER_ERROR}, status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class AllCategories(APIView):
    def get(self, request):
        try:
            categories = Category.objects.values_list('name', flat=True).distinct()
            return Response({"categories": list(categories)}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"response": f"{str(e)}", "status": status.HTTP_500_INTERNAL_SERVER_ERROR}, status.HTTP_500_INTERNAL_SERVER_ERROR)


class PriceRange(APIView):
    def get(self, request):
        try:
            min_price = Product.objects.aggregate(min_price=Min('selling_price'))['min_price']
            max_price = Product.objects.aggregate(max_price=Max('selling_price'))['max_price']
            return Response({"min_price": min_price, "max_price": max_price}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"response": f"{str(e)}", "status": status.HTTP_500_INTERNAL_SERVER_ERROR}, status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class AverageRating(APIView):
    def get(self, request):
        try:
            average_rating = Product.objects.values_list('average_rating',flat=True).distinct().order_by(F('average_rating').desc(nulls_last=True))          
            return Response({"average_rating": average_rating}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"response": f"{str(e)}", "status": status.HTTP_500_INTERNAL_SERVER_ERROR}, status.HTTP_500_INTERNAL_SERVER_ERROR)


class PurchaseProduct(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Purchase A product",
        operation_summary="Purchase A product",
        tags=['Purchase'],
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER,
                              type=openapi.TYPE_STRING)
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'product_id': openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            status.HTTP_201_CREATED: "Food category added successfully",
            status.HTTP_400_BAD_REQUEST: "Invalid data provided",
        }
    )

    
    def post(self, request):
        user = request.user

        try:
            data = request.data
            product_id = data.get('product_id')

            # Retrieve the product by ID
            product = Product.objects.filter(pid=product_id).first()  # Use .first() to get a single object

            if product is None:
                return Response({"response": "Product not found", "status": status.HTTP_404_NOT_FOUND}, status.HTTP_404_NOT_FOUND)

            # Create a purchase history entry
            purchase_history_data = {'user': user.id, 'product': product.id}
            purchase_history_serializer = PurchaseHistorySerializer(data=purchase_history_data)

            if purchase_history_serializer.is_valid():
                purchase_history_serializer.save()
                return Response({"response": "Product purchased successfully", "status": status.HTTP_201_CREATED}, status.HTTP_201_CREATED)
            else:
                return Response({"response": purchase_history_serializer.errors, "status": status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"response": str(e), "status": status.HTTP_500_INTERNAL_SERVER_ERROR}, status.HTTP_500_INTERNAL_SERVER_ERROR)



class ItemBasedRecommendationAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Product recommendation",
        operation_summary="Product recommendation",
        tags=['Product Recommendation'],
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, type=openapi.TYPE_STRING)
        ],
        responses={
            status.HTTP_200_OK: "Product recommendations retrieved successfully",
            status.HTTP_400_BAD_REQUEST: "Invalid data provided",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error",
        }
    )
    def get(self, request):
        try:
            # Get user from the request (assuming the user is authenticated)
            user = request.user

            # Get user's last 5 purchase history
            last_5_purchases = PurchaseHistory.objects.filter(user=user.id).order_by('-purchase_date')[:5]

            if not last_5_purchases.exists():
                return Response({"response": "No purchase history available for the user", "status": "error"}, status=status.HTTP_400_BAD_REQUEST)

            # Get the pid of the last 5 purchases
            last_5_item_pids = [purchase.product.pid for purchase in last_5_purchases]
            print(last_5_item_pids)
            
            result=[]
            for i in range(len(last_5_item_pids)):

                # Get item-based recommendations based on the last 5 purchases
                recommendations = get_recommendations(last_5_item_pids[i])
                result.append(recommendations)
                # print(result)
            

            # Serialize recommendations
            # print(result)
            

            # Return serialized recommendations
            return Response({"response": result, "status": "success"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"response": str(e), "status": "error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ContentBasedRecommendationAPI(APIView):
    def get(self, request):
        try:
            # Get parameters from the request
            rating = request.query_params.get('rating')
            brand = request.query_params.get('brand')
            category = request.query_params.get('category')
            discount = request.query_params.get('discount')
            seller = request.query_params.get('seller')
            selling_price = request.query_params.get('selling_price')
            subcategory = request.query_params.get('subcategory')

            # Get content-based recommendations
            recommendations = get_recommendations_by_inputs(
                rating=rating,
                brand=brand,
                category=category,
                discount=discount,
                seller=seller,
                selling_price=selling_price,
                subcategory=subcategory
            )

            # Serialize recommendations
            serializer = RecommendationSerializer(recommendations, many=True)

            # Return serialized recommendations
            return Response({"response": serializer.data, "status": "success"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"response": str(e), "status": "error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


