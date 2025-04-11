from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import RegisterView
from .views import CustomTokenObtainPairView
from .views import BookViewSet
from .views import book_list_view
from .views import UserViewSet
from .views import BorrowRecordViewSet
from .views import borrow_book_view
from .views import borrow_record_view
from .views import return_book_view
from .views import renew_book_view
from .views import ReviewLogView
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

router = DefaultRouter()

router.register(r'book', BookViewSet,basename='book')

router.register(r'borrow', BorrowRecordViewSet,basename='borrow')

router.register(r'users', UserViewSet,basename='user')

router.register(r'review',ReviewLogView,basename='review')

urlpatterns = [
    path('', include(router.urls)),

    path('register/',RegisterView.as_view()),

    path('book-list/', book_list_view, name='book-list'),

    path('borrow_book/',borrow_book_view,name='borrow_book'),

    path('borrow_record/',borrow_record_view,name='borrow_record'),

    path('returnbook/',return_book_view,name='return-book'),
    path('renewbook/',renew_book_view,name='renew_book'),



    path('auth/',include([
        path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    ])),
]


