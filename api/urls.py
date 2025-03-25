from django.urls import path
from .views import RegisterView, LoginView, SearchByNameView, SearchByPhoneView, PersonDetailView, SpamReportView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('search/name/', SearchByNameView.as_view(), name='search-by-name'),
    path('search/phone/', SearchByPhoneView.as_view(), name='search-by-phone'),
    path('person/<int:identifier>/', PersonDetailView.as_view(), name='person-detail'),
    path('spam/', SpamReportView.as_view(), name='spam-report'),
]
