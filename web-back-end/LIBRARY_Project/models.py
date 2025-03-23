from django.db import models
from django.db.models import CharField


class Book(models.Model):
    ID=models.AutoField(
        verbose_name='编号',
        primary_key=True,
        auto_created=True,
        serialize=False,
    )
    title=models.CharField('书名',max_length=200)
    author=models.CharField('作者',max_length=200)
    description=models.TextField('描述')
    status=models.CharField('状态',max_length=20,choices=[
        ('在库','在库'),
        ('借出','借出')
    ],default='在库')
    stock_quantity=models.IntegerField('库存数量',default=0)
    borrow_quantity=models.IntegerField('借阅数量')



class Uer(models.Model):
    ID = models.AutoField(
        verbose_name='用户ID',
        primary_key=True,
        auto_created=True,
        serialize=False,
    )
    username=CharField('用户名',max_length=15)
    password=CharField('密码',max_length=20)
    Registration_date=models.DateTimeField(
        verbose_name='注册日期',
        auto_now_add=True
    )

