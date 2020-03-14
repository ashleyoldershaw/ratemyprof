from django.urls import path

from . import views

app_name = 'polls'

urlpatterns = [
    path('register', views.register),
    path('login', views.login_user),
    path('logout', views.logout_user),
    path('list', views.list_modules),
    path('view_ratings', views.view_ratings),
    path('average', views.average_rating_per_module),
    path('rate', views.RateProf.as_view()),
]
