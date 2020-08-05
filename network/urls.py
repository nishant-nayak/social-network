from django.urls import path

from . import views

urlpatterns = [
    path("", views.reidx, name="default"),
    path("<int:page>", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("user/<str:name>", views.reuser, name="reuser"),
    path("user/<str:name>/<int:page>", views.userpage, name="userpage"),
    path("following", views.refollow, name="refollow"),
    path("following/<int:page>", views.following, name="following"),

    # API routes
    path("newpost", views.newpost, name="viewpost"),
    path("follow", views.follow, name="follow"),
    path("editpost", views.editpost, name="editpost"),
    path("likepost", views.likepost, name="likepost")
]
