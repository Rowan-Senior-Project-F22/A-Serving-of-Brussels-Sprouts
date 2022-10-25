from django.urls import path
from . import views

app_name = 'recommender'

urlpatterns = [
    path("", views.get_landing_guest, name="get_landing_guest"),
    path("profile/", views.user_profile , name="user_profile"),
    path("playlist/<int:user_id>", views.user_playlist, name="profile"),
]
 