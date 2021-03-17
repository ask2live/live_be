from django.db import models
from django.db.models import IntegerField, Model
from users import models as user_models
from core import models as core_model
from django_mysql.models import ListTextField,ListF
# Create your models here.


class Hole(core_model.AbstractTimeStamp):
    STATUS_NOTSTART = "NOT_START"
    STATUS_DOING = "DOING"
    STATUS_DONE = "DONE"
    STATUS_CHOICES = (
        (STATUS_NOTSTART, "NOT_START"),
        (STATUS_DOING, "DOING"),
        (STATUS_DONE, "DONE"),
    )
    title           = models.CharField(max_length=200)    # 세션 제목
    subtitle        = models.CharField(max_length=400) # 세션 부제
    description     = models.TextField()            # 세션 설명
    reserve_date    = models.DateTimeField(blank=True, null=True) # 세션 시작하는 날짜
    finish_date     = models.DateTimeField(blank=True, null = True) # 세션이 종료되는 날짜    

    status          = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_NOTSTART)
    rating          = models.IntegerField(blank=True, default=0)
    # ====================== 나중에 models.ForeignKey로 변경 ======================
    host            = models.ForeignKey("users.User", related_name="hole",on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title


class LiveHole(core_model.AbstractTimeStamp):
    hole = models.OneToOneField(Hole,related_name="liveholes", on_delete=models.CASCADE, blank=True)
    # participants = models.ManyToManyField("users.User", related_name="liveholes_participants",blank=True) #null이 들어가도 되는건가?
    # host = models.ForeignKey("users.User", related_name="liveholes_host", on_delete=models.CASCADE)
    host_uid = models.IntegerField(blank=True,default=0)
    audience_list = ListTextField( base_field=IntegerField(), size=30,default='')
    # Maximum of 30 ids in list
    room_number = models.CharField(max_length=50,unique=True,default='')

    # def __str__(self):
    #     usernames = []
    #     all_member = self.participants.all()
    #     for member in all_member:
    #         usernames.append(member.email)
    #     return ", ".join(usernames)

    def audience_append(self, uid):
        audience_list=ListF('audience_list').append(uid)
        print(audience_list)
        return audience_list



class Question(core_model.AbstractTimeStamp):
    user = models.ForeignKey("users.User", related_name="questions", on_delete=models.CASCADE)
    hole = models.ForeignKey(Hole, related_name="questions", on_delete=models.CASCADE)
    question = models.TextField(blank=True, default="")
