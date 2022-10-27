from django.urls import path
from .views import CreateThread, ListThreads,ThreadView,CreateMessage
from .import views
from django.contrib.auth import views as auth_views


urlpatterns = [
     path('' ,views.frontpage, name = 'frontpage'),
     path('signup/', views.signup, name = 'signup'),
    path('login/', auth_views.LoginView.as_view(template_name = 'recommender/login.html')),
    path('logout/', auth_views.LogoutView.as_view(), name = 'logout'),
    path('artist/', views.get_artist, name='get_artist'),
    path('album/', views.get_album, name='get_album'),
    path('inbox/', ListThreads.as_view(), name = 'inbox'),
    path('inbox/create-thread', CreateThread.as_view(), name= 'create-thread'),
    path('inbox/<int:pk>', ThreadView.as_view(), name = 'thread'),
    path('inbox/<int:pk>/create-message', CreateMessage.as_view(), name = 'create-message'),
]
 