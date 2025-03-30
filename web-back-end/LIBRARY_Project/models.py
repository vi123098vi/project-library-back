from django.db import models
from django.contrib.auth.models import AbstractUser


class Book(models.Model):
    id = models.AutoField(primary_key=True)
    title=models.CharField('书名',max_length=200)
    author=models.CharField('作者',max_length=200)
    isbn=models.CharField('ISBN', max_length=13, default='0000000000000')
    description=models.TextField('描述')
    status=models.CharField('状态',max_length=20,choices=[
        ('在库','在库'),
        ('借出','借出')
    ],default='在库')
    total_copies = models.IntegerField('总库存数量',default=0)
    stock_quantity=models.IntegerField('库存数量',default=0)
    borrow_quantity=models.IntegerField('借阅数量',default=0)



class User(AbstractUser):
    is_staff = models.BooleanField(default=False) # 管理员标识
    is_active=models.BooleanField(default=True) # 用户状态
    phone=models.CharField('手机号码',max_length=20,blank=True)


class BorrowRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateTimeField('借阅日期',auto_now_add=True)
    due_date = models.DateTimeField('应还日期')
    return_date = models.DateTimeField('归还日期',null=True, blank=True)
    STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('rejected', '已拒绝'),
        ('returned', '已归还')
    ]
    status = models.CharField('借阅状态',max_length=10, choices=STATUS_CHOICES, default='borrowed')


class ReviewLog(models.Model):
    ACTION_CHOICES = [
        ('approve', '通过借阅'),
        ('reject', '拒绝借阅'),
        ('disable_user', '禁用用户'),
        ('enable_user', '启用用户')
    ]

    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_actions')
    borrow_record = models.ForeignKey(BorrowRecord, null=True, on_delete=models.SET_NULL)  # 关联借阅记录
    affected_user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)  # 被操作用户
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    comment = models.TextField(blank=True)  # 审核意见
    timestamp = models.DateTimeField(auto_now_add=True)


class BookLog(models.Model):
    ACTION_CHOICES = [
        ('create', '新增图书'),
        ('update', '修改图书'),
        ('delete', '删除图书')
    ]

    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    before_snapshot = models.JSONField()  # 修改前的数据快照
    after_snapshot = models.JSONField()  # 修改后的数据快照
    timestamp = models.DateTimeField(auto_now_add=True)

class Statistics(models.Model):
    date = models.DateField(unique=True)                      # 统计日期
    top_books = models.JSONField()                             # 当日借阅量Top10图书ID
    total_borrows = models.IntegerField(default=0)            # 当日总借阅量
    active_users = models.IntegerField(default=0)              # 当日活跃用户数