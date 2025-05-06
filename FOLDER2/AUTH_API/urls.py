from django.urls import path
from . import views
from .views import feedback_before_logout

urlpatterns = [
    path('login/', views.login_view, name='login'),        # ✅ this name is important
    path('signup/', views.signup_view, name='signup'),
    path('logout/', feedback_before_logout, name='logout'),  # ⬅️ updated to use feedback view
    path('', views.home_view, name='home'),
    path('about-us/', views.about_us, name='about_us'),

    
]
