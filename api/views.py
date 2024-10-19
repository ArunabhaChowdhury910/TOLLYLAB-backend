from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from .models import Product, Order  # Replace with your actual model name
from .serializers import ProductSerializer  # Replace with your actual serializer
from .models import Testimonial 
from rest_framework import status
from .serializers import OrderSerializer
from django.core.mail import send_mail


from django.http import Http404, HttpResponse
from rest_framework import generics
from .models import GalleryImage
from .serializers import GalleryImageSerializer

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
import json


from rest_framework.decorators import api_view

class GroupedGalleryImagesView(APIView):
    def get(self, request):
        images = GalleryImage.objects.all()
        serializer = GalleryImageSerializer(images, many=True)
        return Response(serializer.data)
        # landscape_images = [image for image in images if image.orientation == 'landscape']
        # portrait_images = [image for image in images if image.orientation == 'portrait']

        # # Group images according to the specified rules
        # grouped_images = []
        # index = 0

        # while index < len(portrait_images):
        #     if index + 3 < len(portrait_images):
        #         grouped_images.append(portrait_images[index:index+4])
        #         index += 4
        #     else:
        #         grouped_images.append(portrait_images[index:])
        #         break

        # for i in range(0, len(landscape_images), 2):
        #     if i + 1 < len(landscape_images):
        #         grouped_images.append(landscape_images[i:i+2])
        #     else:
        #         grouped_images.append([landscape_images[i]])

        # # Flatten the grouped images for serialization
        # flat_grouped_images = [image for group in grouped_images for image in group]

        # serializer = GalleryImageSerializer(flat_grouped_images, many=True)
        # return Response(serializer.data)

@api_view(['GET'])
def grouped_images(request):
    images = GalleryImage.objects.all()
    
    grouped_images = []
    group = []
    current_row_width = 0

    for image in images:
        if image.orientation == 'landscape':
            group.append(image)
            current_row_width += 2
        else:
            group.append(image)
            current_row_width += 1
        
        if current_row_width >= 4:
            grouped_images.append(group)
            group = []
            current_row_width = 0

    if group:
        grouped_images.append(group)
    
    serializer = GalleryImageSerializer(grouped_images, many=True)
    return Response(serializer.data)

class GalleryImageListView(generics.ListAPIView):
    queryset = GalleryImage.objects.all()
    serializer_class = GalleryImageSerializer

def index(request):
    return HttpResponse("Hello, world. You're at the index.")

class ProductListView(APIView):
    def get(self, request):
        products = Product.objects.all()  # Fetch all products
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class ProductDetailView(APIView):
    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        product = self.get_object(pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        product = self.get_object(pk)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        product = self.get_object(pk)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

# api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Testimonial  # Replace with your actual model name
from .serializers import TestimonialSerializer  # Replace with your actual serializer

class TestimonialListView(APIView):
    def get(self, request):
        testimonials = Testimonial.objects.all()  # Fetch all testimonials
        serializer = TestimonialSerializer(testimonials, many=True)
        return Response(serializer.data)
    
class TestimonialDetailView(APIView):
    def get_object(self, pk):
        try:
            return Testimonial.objects.get(pk=pk)
        except Testimonial.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        testimonial = self.get_object(pk)
        serializer = TestimonialSerializer(testimonial)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        testimonial = self.get_object(pk)
        serializer = TestimonialSerializer(testimonial, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        testimonial = self.get_object(pk)
        testimonial.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

from rest_framework_simplejwt.tokens import RefreshToken

class RegisterView(APIView):
    def post(self, request):
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email = request.data.get('email')
        password = request.data.get('password')

        if not first_name or not last_name or not email or not password:
            return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=email).exists():
            return Response({"error": "Email is already in use"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=email, first_name=first_name, last_name=last_name, email=email, password=password)
        
        refresh = RefreshToken.for_user(user)
        
        
        response = Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        response.set_cookie(
            key='access_token',
            value=str(refresh.access_token),
            httponly=True,  # This makes it HTTP-only
            secure=True,  # This ensures the cookie is only sent over HTTPS
            samesite='Lax',  # This adds CSRF protection
            max_age=3600,  # Expires after 1 hour
        )
        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,  # This makes it HTTP-only
            secure=True,  # Only sent over HTTPS
            samesite='Lax',
            max_age=86400,  # Expires after 1 day
        )
        
        return response

from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(username=email, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)

            response = Response({"message": "Logged in successfully"}, status=status.HTTP_200_OK)
            response.set_cookie(
                key='access_token',
                value=str(refresh.access_token),
                httponly=True,
                secure=True,
                samesite='Lax',
                max_age=3600,
            )
            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                secure=True,
                samesite='Lax',
                max_age=86400,
            )
            return response
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from django.utils.http import urlsafe_base64_decode
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status


class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

        token = PasswordResetTokenGenerator().make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_url = f"http://localhost:3000/reset-password/{uid}/{token}"

        email_subject = 'Password Reset Request'
        email_body = render_to_string('password_reset_email.html', {'reset_url': reset_url})

        send_mail(email_subject, email_body, 'from@example.com', [email])

        return Response({"message": "Password reset link has been sent to your email."}, status=status.HTTP_200_OK)


from django.contrib.auth.tokens import default_token_generator

class ResetPasswordView(APIView):
    def post(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Token has expired."}, status=status.HTTP_400_BAD_REQUEST)

        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if new_password != confirm_password:
            return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)



from rest_framework.permissions import IsAuthenticated

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if not user.check_password(old_password):
            return Response({"error": "Old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({"message": "Password has been changed successfully."}, status=status.HTTP_200_OK)



from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import UserProfileSerializer

# Profile View
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    user = request.user
    serializer = UserProfileSerializer(user)
    return Response(serializer.data)

    
from django.core.mail import send_mail
from .models import Product,Order
class CheckoutView(APIView):
    def post(self, request):
        # Extract product details from the request
        product_name = request.data.get('product_name')
        product_price = request.data.get('product_price')
        quantity = request.data.get('quantity')
        shipping_address = request.data.get('shipping_address')
        customer_name = request.data.get('customer_name')
        email = request.data.get('email')
        phone = request.data.get('phone')
        address = request.data.get('address')
        postal_code = request.data.get('postal_code')
        city = request.data.get('city')
        country = request.data.get('country')
        
        if not shipping_address:
            return Response({'error': 'Shipping address is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(name=product_name)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if enough stock is available
        if product.stock < quantity:
            return Response({'error': 'Not enough stock available'}, status=status.HTTP_400_BAD_REQUEST)

        # Deduct the quantity from the current stock
        product.stock -= quantity
        total_price = (product_price * quantity)
        product.save()  # Save the updated stock back to the database

        order = Order.objects.create(
            customer_name=customer_name,
            email=email,
            phone=phone,
            address=address,
            postal_code=postal_code,
            city=city,
            country=country,
            product=product,
            quantity=quantity,
            total_price=total_price
        )
        order.save()
        
        # Compose email content
        subject = 'New Order Received'
        message = (
            f"Customer Name: {customer_name}\n"
            f"Email: {email}\n"
            f"Phone: {phone}\n"
            f"Product: {product_name}\n"
            f"Price: {product_price}\n"
            f"Quantity: {quantity}\n"
            f"Total Price: {total_price}\n"
            f"Shipping Address: {shipping_address}\n"  # Include shipping address in the email
        )
        admin_email = 'mailtoarunabha1234.e@gmail.com'

        # Send email
        try:
            send_mail(
                subject,
                message,
                'e82378899@gmail.com',  # From email
                [admin_email],  # To email
            )
            return Response({'message': 'Email sent successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import JsonResponse, HttpResponse

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
@api_view(['POST'])
def create_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        # amount = int(request.POST.get('amount'))  # amount should be in paise (i.e., 100 = 1 INR)
        amount = int(data.get('amount'))
        
        if not amount:
            return Response({'error': 'Amount is required'}, status=status.HTTP_400_BAD_REQUEST)

        
        try:
            
            # Create an order in Razorpay
            razorpay_order = razorpay_client.order.create({
                'amount': amount,  # Amount in paise
                'currency': 'INR',
                'payment_capture': '1'  # Auto-capture the payment
            })
            # order = razorpay_client.order.create(order_data)
            
            return JsonResponse({
                'order_id': razorpay_order['id'],
                'amount': razorpay_order['amount'],
                'currency': razorpay_order['currency'],
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    # return HttpResponse('Invalid request method', status=405)

# views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import razorpay
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)




@csrf_exempt
@api_view(['POST'])
def payment_success(request):
    if request.method == 'POST':
        try:
            data = request.data
            payment_id = data.get('razorpay_payment_id')
            order_id = data.get('razorpay_order_id')
            signature = data.get('razorpay_signature')
            
            
            logger.info(f"Received payment data: payment_id={payment_id}, order_id={order_id}")
            
            # print('hey what is going on', payment_id, order_id, signature)

            # Verify the payment signature to confirm the payment
            razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            try:
                razorpay_client.utility.verify_payment_signature(params_dict)
            except razorpay.errors.SignatureVerificationError as e:
                logger.error(f"Signature verification failed: {str(e)}")
                return Response({'error': 'Razorpay Signature Verification Failed'}, status=400)

            logger.info("Payment signature verified successfully")
            
            razorpay_client.utility.verify_payment_signature(params_dict)
            
            product_name = request.data.get('product_name')
            product_price = float(request.data.get('product_price'))
            quantity = int(request.data.get('quantity'))
            shipping_address = request.data.get('shipping_address')
            customer_name = request.data.get('customer_name')
            email = request.data.get('email')
            phone = request.data.get('phone')
            
            try:
                product = Product.objects.get(name=product_name)
                total_price = product_price * quantity

                order = Order.objects.create(
                    customer_name=customer_name,
                    email=email,
                    phone=phone,
                    address=shipping_address,
                    product=product,
                    quantity=quantity,
                    total_price=total_price
                )
                order.save()
                
                product.stock -= quantity
                product.save()

                # Send email
                subject = 'New Order Received'
                message = f"""
                Customer Name: {customer_name}
                Email: {email}
                Phone: {phone}
                Product: {product_name}
                Price: {product_price}
                Quantity: {quantity}
                Total Price: {total_price}
                Shipping Address: {shipping_address}
                """
                
                user_subject = "Order Confirmation"
                user_message = (
                f"Dear {customer_name},\n\n"
                f"Thank you for your order. Here are the details of your purchase:\n"
                f"Product: {product_name}\n"
                f"Price: Rs. {product_price}\n"
                f"Quantity: {quantity}\n"
                f"Total Price: Rs. {total_price}\n"
                f"Shipping Address: {shipping_address}\n\n"
                f"We will notify you once your order is shipped.\n"
                f"Best regards,\n"
                f"The TOLLYLAB Team"
                )
                
                
                admin_email = 'mailtoarunabha1234.e@gmail.com'

                send_mail(
                    subject,
                    message,
                    'e82378899@gmail.com',  # From email
                    [admin_email],  # To email
                )
                
                send_mail(
                user_subject,
                user_message,
                settings.DEFAULT_FROM_EMAIL,  # From email
                [email],  # User's email
                fail_silently=False,
            )
                
                return Response({'status': 'success', 'message': 'Payment successful and order created'})
            except Product.DoesNotExist:
                return Response({'error': 'Product not found'}, status=404)
            except Exception as e:
                return Response({'error': str(e)}, status=500)

        except Exception as e:
            return Response({'error': str(e)}, status=400)

            # Check if the signature is valid
            # result = razorpay_client.utility.verify_payment_signature(params_dict)

            # if result is None:
            #     # Signature is valid, proceed with your logic
            #     return JsonResponse({'status': 'success'})
            # else:
            #     # Signature is invalid
            #     return JsonResponse({'error': 'Invalid signature'}, status=400)

        # except Exception as e:
        #     return JsonResponse({'error': str(e)}, status=500)
    
    # return HttpResponse('Invalid request method', status=405)


@csrf_exempt
def store_product_in_session(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data sent from the frontend
            data = json.loads(request.body)
            name = data.get('name')
            price = data.get('price')
            quantity = data.get('quantity')

            # Log received data
            # print(f"Received Product Data: Name: {name}, Price: {price}, Quantity: {quantity}")

            if not name or not price:
                return JsonResponse({"error": "Product name and price are required."}, status=400)
            
            # Store product name and price in the session
            request.session['product_Name'] = name
            request.session['product_price'] = price
            request.session['product_quantity'] = quantity

            return JsonResponse({"message": "Product stored in session successfully"})
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid request method."}, status=400)




# Fetch the product details stored in the session
# In your views.py ISSUE HERE
def get_product_from_session(request):
    product_name = request.session.get('product_name', 'Unknown Product')
    product_price = request.session.get('product_price',0.0 )
    product_quantity = request.session.get('product_quantity', 1)  # Default to 1

    # Log to confirm the data retrieval
    print(f"Product from session: Name: {product_name}, Price: {product_price}, Quantity: {product_quantity}")

    return JsonResponse({
        "name": product_name,
        "price": product_price,
        "quantity": product_quantity
    })





# views.py (Checkout view)
def checkout(request):
    product_name = request.session.get('product_name')
    product_price = request.session.get('product_price')
    product_quantity = request.session.get('product_quantity')

    return JsonResponse({
        'name': product_name,
        'price': product_price,
        'quantity': product_quantity
    })

