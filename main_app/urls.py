from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('about/', views.about, name='about'),
    path('accounts/signup/', views.signup, name='signup'),
    path('boards/', views.boards_index, name='boards_index'),
    path('boards/<int:board_id>/', views.boards_detail, name='boards_detail'),
    path('boards/create/', views.BoardCreate.as_view(), name='boards_create'),
    path('boards/<int:pk>/update/', views.BoardUpdate.as_view(), name='boards_update'),
    path('boards/<int:pk>/delete/', views.BoardDelete.as_view(), name='boards_delete'),
]
