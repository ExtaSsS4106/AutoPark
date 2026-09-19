from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from .views import (
    RegisterView, ProfileView, LogoutView,
    AllUsers,AmIsuperUser, ProfileInfo, ErrorResponse, SellCar, AcceptCar, GetCars
)
urlpatterns = [
    path('', ErrorResponse.as_view(), name='error-response'),
    
    path('api/profile-info/', ProfileInfo.as_view(), name='profile-info'),
    
    path('api/amisuperuser/', AmIsuperUser.as_view(), name='register'),

    path('api/register/', RegisterView.as_view(), name='register'),
    
    path('api/profile/', ProfileView.as_view(), name='profile'),
    
    path('api/logout/', LogoutView.as_view(), name='logout'),
    
    path('api/all-users/', AllUsers.as_view(), name='all-users'),


    path('api/SellCar/', SellCar.as_view(), name='sell-car'),
    path('api/AcceptCar/', AcceptCar.as_view(), name='accept-car'),
    path('api/GetCars/', GetCars.as_view(), name='get-cars'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
