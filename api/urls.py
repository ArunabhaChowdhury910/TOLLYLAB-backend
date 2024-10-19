from django.urls import path
from . import views
from .views import RegisterView, GalleryImageListView, grouped_images, GroupedGalleryImagesView, ProductListView, ProductDetailView, TestimonialListView, TestimonialDetailView, CheckoutView, profile_view, RegisterView, LoginView, create_order, ForgotPasswordView, ResetPasswordView, ChangePasswordView

urlpatterns = [
    
    path('products/', ProductListView.as_view(), name='product-list'),  # Product list view
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),  # Product detail view
    path('testimonials/', TestimonialListView.as_view(), name='testimonial-list'),  # Testimonial list view
    path('testimonials/<int:pk>/', TestimonialDetailView.as_view(), name='testimonial-detail'),  # Testimonial detail view
    path('register/', RegisterView.as_view(), name='register'),  # User registration view
    path('gallery/images/', GalleryImageListView.as_view(), name='gallery-image-list'),
    path('gallery/images/grouped/', GroupedGalleryImagesView.as_view(), name='grouped_gallery_images'),
    path('gallery/images/grouped-list/', grouped_images, name='grouped-images'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('profile/', profile_view, name='profile'),  # Profile view endpoint
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('store_product/', views.store_product_in_session, name='store_product'),
    path('get_product/', views.get_product_from_session, name='get_product'),
    path('create-order/', create_order, name='create_order'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/<uidb64>/<token>/', ResetPasswordView.as_view(), name='reset-password'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    
]
