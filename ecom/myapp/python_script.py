from django.shortcuts import render
from django.http import HttpResponse
from .ecom7 import *
import joblib
import os
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.shortcuts import render

from .models import *

from rest_framework_simplejwt.tokens import RefreshToken

import random
from django.conf import settings
from django.core.mail import send_mail
import csv
from datetime import datetime 
import requests
import requests
import openai
from .serializer import *
from myapp.python_script import *





api_url="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"
BASE_URL='http://127.0.0.1:8000/'

file_dir = os.path.dirname(__file__)
model_path = os.path.join(file_dir, 'ecommerce.joblib')

# Check if the file exists before attempting to load it
if os.path.exists(model_path):
    loaded_model = joblib.load(model_path)
else:
    print(f"Error: Model file '{model_path}' not found.")
    loaded_model = None



def get_content_based_recommendations(request):
    if request.method == 'POST':
        try:
            # Get parameters from the request
            rating = request.POST.get('rating')
            brand = request.POST.get('brand')
            category = request.POST.get('category')
            selling_price = request.POST.get('priceValue')
            subcategory = request.POST.get('subcategory')
            
            
            if brand == 'Select':
                brand = None
            if category == 'Select':
                category = None
            if selling_price == 'Select':
                selling_price = None
            if subcategory == 'Select':
                subcategory = None

            # Validate that at least one parameter is not None
            if all(value is None for value in [rating, brand, category, selling_price, subcategory]):
                raise ValueError("At least one parameter must not be None")
                    
        
            # Validate that at least one parameter is not None
            
            data = {
                'rating': rating,
                'brand': brand,
                'category': category,
                'selling_price': selling_price,
                'subcategory': subcategory
            }
            print(data)

            # Get content-based recommendations
            recommendations = get_recommendations_by_inputs(
                rating=rating,
                brand=brand,
                category=category,
                selling_price=selling_price,
                subcategory=subcategory
            )
            # Convert DataFrame to JSON
            recommendations_dict = recommendations.to_dict(orient='records')

            print(recommendations_dict)
            # Return dictionary as JSON response
            return render(request,'home.html', {"response":recommendations_dict })

        except Exception as e:
            return render(request,'home.html', {"error":f"error{str(e)}" })

    return render(request,'home.html', {"error":"error" })






def get_item_based_recommendations(request):
    if request.method == 'GET':
        try:
            
            token = request.session.get('access_token')

            if token:
                headers = {'Authorization': f'Bearer {token}'}
            api_url = f'{BASE_URL}Recomendation/'  # Replace with your actual API endpoint URL


            response = requests.get(api_url, headers=headers)

            if response.status_code == 200:
                recommendations = response.json()
                
                
                new_dictionary = {'status': recommendations['status']}
                new_dictionary['recommendations'] = []
                    
                for item in recommendations['response']:
                    image_links = [link[2:-2] for link in item['images']]
                    new_item = {
                        'title': item['title'],
                        'brand': item['brand'],
                        'category': item['category'],
                        'actual_price': item['actual_price'],
                        'discount': item['discount'],
                        'images': image_links,
                        'url': item['url'],
                        'rating':item['average_rating'],
                        'description':item['description'],
                        'seller':item['seller'],
                        'product_details':item['product_details']
                    }
                    
                    new_dictionary['recommendations'].append(new_item)
                    print("this is image : ",image_links)
                
                response_data=[]
                a=1
                for i in new_item['discount']:
                
                    x=chatbot(a,i)
                    response_data.append(x)
                    a+=1
                
                dict2={"answer":response_data}
                print(dict2)
                            
                return render(request, 'home.html', {'recommendations': new_dictionary,"answer":dict2})


            else:
                return render(request, 'home.html', {'error': f"Error: {response.text}"})

        except Exception as e:
            return render(request, 'home.html', {'error': str(e)})

    return render(request, 'home.html')



def chatbot(i,content):
   
    openai.api_key = api_url  

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "assistant", 
                "content": f'Assume you have to recommend the e commerce product recomendation and building a thought in to use mind to consider the product so will provide you products name and Please Provide a response making customer buying {content}, your response should be like as you(user) have recently buy this we have a similar products ,your response must be short by the way.'},
        ]
    )

    response_data = {
        f"answer{i}": response.choices[0].message['content'],
    }
    print(response_data)
    return response_data


def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_email(email, otp):
    subject = 'OTP for user Registration '
    message = f'your otp for Registration is :  {otp}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)


def get_token_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }



def register_all_products(request):
    csv_file_path = 'flipkart1.csv'  # Update with your actual CSV file path

    with open(csv_file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                crawled_at = datetime.strptime(row['crawled_at'], '%m/%d/%Y, %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                out_of_stock = row['out_of_stock'].lower() == 'true'
                
                # Assuming your CSV file has columns corresponding to the Product model fields
                brand, _ = Brand.objects.get_or_create(name=row['brand'])
                category, _ = Category.objects.get_or_create(name=row['category'])
                sub_category, _ = SubCategory.objects.get_or_create(name=row['sub_category'])

                try:
                    average_rating = float(row['average_rating'])
                except ValueError:
                    average_rating = 0.0  #
                    
                decimal_fields = ['actual_price', 'discount', 'selling_price']
                for field in decimal_fields:
                    try:
                        row[field] = float(row[field])
                    except (ValueError):
                        row[field] = float(0.0)  # Set a default value or handle it as needed

                    
                product = Product.objects.create(
                    actual_price=row['actual_price'],
                    average_rating=average_rating,
                    brand=brand,
                    category=category,
                    crawled_at=crawled_at,
                    description=row['description'],
                    discount=row['discount'],
                    images=row['images'],
                    out_of_stock=out_of_stock,
                    pid=row['pid'],
                    product_details=row['product_details'],
                    seller=row['seller'],
                    selling_price=row['selling_price'],
                    sub_category=sub_category,
                    title=row['title']
                )
    return HttpResponse("all Products added")




def index_page(request):
    return render(request,"index.html")


def signup_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        name = request.POST.get('name')
        password = request.POST.get('password')
        address = request.POST.get('address')

        # API endpoint for user registration
        api_url = f'{BASE_URL}Registration/'  # Replace with your actual API endpoint

        # Prepare data for API request
        data = {
            'email': email,
            'name': name,
            'password': password,
            'address': address,
        }

        # Make API request
        try:
            response = requests.post(api_url, data=data)
            response_data = response.json()

            # Check if the registration was successful
            if response.status_code==201:
                context={'request': 'Registration successful. Please check your email to verify your account.'}
                return redirect('verify_email_page')  # Redirect to login page
            else:
                context={'request': 'Error during registration. Please try again'}

        except requests.exceptions.RequestException as e:
            context={'request': f'Error during registration: {str(e)}'}
    return render(request, "sign_up.html")

def verify_email_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        otp = request.POST.get('otp')

        api_url = f'{BASE_URL}VerifyEmail/'  

        data = {
            'email': email,
            'otp': int(otp),
        }

        try:
            response = requests.post(api_url, json=data)
            print(response)
            response_data = response.json()

            # Check if email verification was successful
            if response.status_code==200:
                context={'message':"Email verification successful. You can now log in."}
                return redirect('login_page')  # Redirect to login page
            else:
                context={"message":'Error during email verification. Please try again.'}
        except Exception as e:
            print(e)
            context={'message':f'Error during email verification: {str(e)}'}

    return render(request, "verify_email.html")


def login_user_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        api_url = f'{BASE_URL}Login/'  # Replace with your actual API endpoint

        # Prepare data for API request
        data = {
            'email': email,
            'password': password,
        }

        # Make API request
        try:
            response = requests.post(api_url, data=data)
            response_data = response.json()

            if response.status_code==200:
                context={"message":'Login successful'}
                request.session['user_id'] = response_data.get('Your user id')
                request.session['access_token'] = response_data['token']['access']
                # return redirect('dashboard')  # Redirect to dashboard or home page
                return redirect("get_item_based_recommendations")
            else:
                context={'message':"Error During Login . Please check your credentials"}
        except requests.exceptions.RequestException as e:
            context={'message':f'Error during login{str(e)}'}

    return render(request, "login.html")


def forgot_password_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        api_url = f'{BASE_URL}ForgotPassword/'  # Replace with your actual API endpoint

        data = {
            'email': email,
        }

        try:
            response = requests.post(api_url, data=data)
            response_data = response.json()

            if response.status_code==200:
                context={'message':'Forgot password request successful. Check your email for further instructions.'}

                return redirect('set_new_password_page')  # Redirect to login page
            else:
                context={'message':'Error during forgot password request. Please try again.'}

        except requests.exceptions.RequestException as e:
            context={'message':f'Error during forgot password request: {str(e)}'}


    return render(request, "forgot_password.html")

def set_new_password_page(request):
    if request.method == 'POST':
        # Collect form data
        email = request.POST.get('email')
        otp = request.POST.get('otp')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # API endpoint for setting a new password
        api_url = f'{BASE_URL}SetNewPassword/'  # Replace with your actual API endpoint

        # Prepare data for API request
        data = {
            'email': email,
            'otp': otp,
            'new_password': new_password,
            'confirm_password': confirm_password,
        }

        # Make API request
        try:
            response = requests.post(api_url, data=data)
            response_data = response.json()

            # Check if setting a new password was successful
            if response.status_code==200:
                context={'message':'Password changed successfully. You can now log in with your new password.'}
                return redirect('login_page')  # Redirect to login page
            else:
                context={'message':'Error during password change. Please try again.'}
        except requests.exceptions.RequestException as e:
            context={'message':f'Error during password change: {str(e)}'}

    return render(request, "set_new_password.html")

def home_page(request):
    return render(request,'home.html')


def user_logout(request):
    endpoint = f'{BASE_URL}UserLogout/'  # Replace with the correct URL
    response = requests.get(endpoint)

    if response.status_code == 200:
        return redirect('index_page')
    else:
        return render(request,'index.html')
    
def buy_product(request):
    if request.method == 'GET':
        try:
            # Assuming you have the user's authentication token stored in the session
            token = request.session.get('access_token')

            if token:
                headers = {'Authorization': f'Bearer {token}'}

            # Retrieve the product ID from the query parameters
            product_id = request.GET.get('pid')

            if not product_id:
                return render(request, 'home.html', {'error': 'Product ID is missing'})

            api_url = f'{BASE_URL}purchase/'  # Replace with your actual API endpoint URL

            # Pass the product ID in the request body
            data = {'product_id': product_id}

            response = requests.post(api_url, headers=headers, data=data)

            # Check if the request was successful (status code 201)
            if response.status_code == 201:
                return redirect('get_item_based_recommendations')

            # If the request was not successful, handle the error
            else:
                return redirect('get_content_based_recommendations')

        except Exception as e:
            return redirect('get_content_based_recommendations')

    return redirect('get_content_based_recommendations')
