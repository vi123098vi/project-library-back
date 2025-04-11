from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer
from LIBRARY_Project.models import User, ReviewLog
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        role="admin" if user.is_staff else "user"
        print(f"User role: {role}")
        access = serializer.validated_data['access']
        refresh = serializer.validated_data['refresh']
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'role': role,
            },
            'access_token': access,
            'refresh_token': refresh,
        })

#处理图书列表请求
from .models import Book
from .serializers import BookSerializer
class BookViewSet(viewsets.ModelViewSet):
    queryset=Book.objects.all()
    serializer_class=BookSerializer
    authentication_classes=[JWTAuthentication]
    permission_classes = [IsAuthenticated]

#处理借阅记录请求--所有借阅记录视图（管理员可见）
from .models import BorrowRecord
from .serializers import BorrowRecordSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
class BorrowRecordViewSet(viewsets.ModelViewSet):
    serializer_class=BorrowRecordSerializer
    permission_classes = [IsAuthenticated]

    queryset = BorrowRecord.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            queryset=BorrowRecord.objects.get(status='pending')
            return self.queryset
        return self.queryset.filter(user=user)

    @action(detail=True, methods=['post'],permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        borrow_record = self.get_object()
        if borrow_record.status == 'pending':
            borrow_record.status = 'approved'
            borrow_record.save()
            return Response({'status': 'approved', 'message': 'Record approved successfully.'})
        return Response({'status': 'error', 'message': 'Record is not pending.'}, status=400)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def reject(self, request, pk=None):
        borrow_record = self.get_object()
        if borrow_record.status == 'pending':
            borrow_record.status = 'rejected'
            borrow_record.save()
            return Response({'status': 'rejected', 'message': 'Record rejected successfully.'})
        return Response({'status': 'error', 'message': 'Record is not pending.'}, status=400)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

#图书列表视图请求
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from .serializers import BookListSerializer

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def book_list_view(request):
    books = Book.objects.all()
    serializer = BookListSerializer(books, many=True)
    return Response(serializer.data)


from rest_framework import status
from django.utils import timezone
from datetime import timedelta
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def borrow_book_view(request):
    user = request.user  # 获取当前登录用户
    book_id = request.data.get('bookId')
    # 2. 获取书籍
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return Response({"detail": "书籍不存在"}, status=status.HTTP_404_NOT_FOUND)

    # 3. 判断库存是否充足
    if book.borrow_quantity >= book.stock_quantity:
        return Response({"detail": "该书籍已被借完"}, status=status.HTTP_400_BAD_REQUEST)


    if  BorrowRecord.objects.filter(user=user,book=book,status__in=['pending','borrowed']).exists():
        return Response({"detail": "已借阅过该书籍，请勿重复借阅"}, status=status.HTTP_400_BAD_REQUEST)

    # 4. 创建借阅记录
    borrow_record = BorrowRecord.objects.create(
        user=user,
        book=book,
        status='pending',
        due_date=timezone.now()+timedelta(days=30)
    )
    borrow_record.save()
    # 5. 更新书籍的借阅数量
    book.borrow_quantity += 1
    book.save()
    return Response({"detail": "借阅请求已提交，等待审核"}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def borrow_record_view(request):
    user = request.user
    borrow_records = BorrowRecord.objects.filter(user=user)
    if not borrow_records:
        return Response({"detail": "没有找到借阅记录"}, status=status.HTTP_404_NOT_FOUND)
    data = [
        {
            'book':
                {
                    'title':record.book.title,
                    'id':record.book.id,
                },
            'borrow_date': record.borrow_date,
            'due_date': record.due_date,
            'status': record.status,
        }
        for record in borrow_records
    ]
    print(data)
    return Response(data, status=status.HTTP_200_OK)

from django.db import transaction
@api_view(['POST'])
@transaction.atomic
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def return_book_view(request):
    book_id = request.data.get('bookId')
    if not book_id:
        return Response({"detail": "缺少图书ID"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        borrow_record = BorrowRecord.objects.filter(user=request.user, book_id=book_id, status='borrowed').first()

        if not borrow_record:
            return Response({"detail": "未找到借阅记录或该图书未借阅"}, status=status.HTTP_404_NOT_FOUND)
        borrow_record.status = 'returned'
        borrow_record.return_date = timezone.now()
        borrow_record.save()

        book=borrow_record.book
        book.total_copies+=1
        book.stock_quantity+=1
        book.borrow_quantity -= 1
        book.save()
        return Response({"detail": "图书归还成功"}, status=status.HTTP_200_OK)
    except BorrowRecord.DoesNotExist:
        return Response({"detail": "图书不存在"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@transaction.atomic
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def renew_book_view(request):
    book_id = request.data.get('bookId')
    if not book_id:
        return Response({"detail": "缺少图书ID"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        borrow_record = BorrowRecord.objects.filter(
            user=request.user,
            book_id=book_id,
            status='borrowed'
        ).first()
        if not borrow_record:
            return Response({"detail": "未找到借阅记录或该图书未借阅"}, status=status.HTTP_404_NOT_FOUND)
        if borrow_record.renew_count >= 1:
            return Response({"detail": "已达最大续借次数"}, status=status.HTTP_403_FORBIDDEN)

        borrow_record.renew_count+=1
        borrow_record.due_date=borrow_record.due_date+timedelta(days=30)
        borrow_record.save()
        return Response(
            {
                "detail": "续借成功",
                "new_due_date": borrow_record.due_date,
                "renew_count": borrow_record.renew_count
        }, status=200)
    except Exception as e:
        return Response({"detail": str(e)}, status=500)

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # 保存用户
            return Response({
                "message": "User created successfully!",
                "user": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#借阅记录日志
from .serializers import ReviewLogSerializer
class ReviewLogView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = ReviewLog.objects.all()
    serializer_class = ReviewLogSerializer


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def approve_book_view(request):
    book_id = request.data.get('bookId')
