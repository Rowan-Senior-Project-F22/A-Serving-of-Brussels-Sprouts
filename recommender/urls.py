from django.urls import path
from . import views

app_name = 'recommender'

urlpatterns = [
    path("", views.get_landing_guest, name="get_landing_guest")
]
 