from django.urls import path
from compiler import views

urlpatterns = [
    path("", views.submit_code, name="compiler_playground"),
    path("result/", views.result_page, name="result_page"),
]