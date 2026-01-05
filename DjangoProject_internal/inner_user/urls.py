from django.urls import path
from. import views

urlpatterns = [
    path("register/", views.Register, name="register"),
    path("search_account/", views.SearchAccount, name="search_account"),
    path("delete_account/", views.DeleteAccount, name="delete_account"),
    path("update_account/", views.UpdateAccount, name="update_account"),
    path("login/", views.login_view, name="login"),
    path("check_status/", views.check_status, name="check_status"),
    path("update_password/", views.update_password, name="update_password"),
    path("register_adminter/", views.Register_adminter, name="register_adminter"),
    path("update_password_adminter/", views.update_password_adminter, name="update_password_adminter"),
    path("delete_account_adminter/", views.delete_account_adminter, name="delete_account_adminter"),
    path("logout/", views.logout_view, name="logout")
]