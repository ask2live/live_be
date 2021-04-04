from django.db import models
from django.db.models import IntegerField, BigIntegerField,Model
from users import models as user_models
from core import models as core_model

from django_mysql.models import ListTextField
from django.db.models import Q
from django_mysql.models import ListTextField,ListF
from django.core.exceptions import ValidationError
# Create your models here.

# class HoleQuerySet(models.QuerySet):
    
#     def search(self, query=None):
#         queryset = self
#         if query is not None:
#             or_lookup = (Q(title__icontains=query) |
#                         Q(subtitle__icontains=query) |
#                         Q(description__icontains=query) &
#                         Q(status__icontains=query)
#                         )
#             queryset = queryset.filter(or_lookup).distinct()
#         return queryset

# class HoleManager(models.Manager):

#     def get_queryset(self):
#         return HoleQuerySet(self.model, using=self._db)
    
#     def search(self, query=None):
#         return self.get_queryset().search(query=query)


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
    description     = models.TextField()            # 세션 설명
    reserve_date    = models.DateTimeField(blank=True, null=True) # 세션 시작하는 날짜
    finish_date     = models.DateTimeField(blank=True, null = True) # 세션이 종료되는 날짜    
    status          = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_NOTSTART)
    host            = models.ForeignKey("users.User", related_name="hole",on_delete=models.CASCADE)
    # rating          = models.IntegerField(blank=True, default=0)
    # objects = HoleManager()
    
    def __str__(self):
        return self.title

    @property
    def count_participant(self):
        users = self.liveholes.participants.filter(leaved__isnull=True)
        # print("users : ",users)
        # print(users.count())
        return users.count()
    @property
    def count_questions(self):
        questions = self.questions.all()
        return questions.count()


class LiveHole(core_model.AbstractTimeStamp):
    id = models.CharField(max_length=100,primary_key=True, unique=True) # id를 channel number로 바꿔야 할듯.
    hole = models.OneToOneField(Hole,related_name="liveholes", on_delete=models.CASCADE, blank=True)
    # 언제 pariticpant가 join했는지 알려면 테이블을 따로 빼서 ForeignKey로 둬야 할지도..
    # participants = models.ManyToManyField("users.User", related_name="liveholes_participants",blank=True, default='') #null이 들어가도 되는건가?
    host_uid = models.BigIntegerField(blank=True,default=0) # User에 uid를 넣어놓을거면 사실 여기서 직접 필드 설정할 필요는 없을듯. 숫자가 커서 Bigint 썼는데 DecimalField 써보라는 의견도 있음.
    audience_uids = ListTextField( base_field=BigIntegerField(), size=30,default='',blank=True)
    # Maximum of 30 ids in list



# particiapants를 따로 클래스로 만드는게 나을듯.
class Participants(models.Model):
    livehole = models.ForeignKey(LiveHole, on_delete=models.CASCADE, related_name="participants")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="participants")
    joined= models.DateTimeField(auto_now_add=True,editable=False, blank=True)
    leaved = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return str(self.user)
    
    def clean(self):
        if Participants.objects.filter(user=self.user, leaved__isnull=False).exists():
            raise ValidationError("a user already exists!")



class Question(core_model.AbstractTimeStamp):
    user = models.ForeignKey("users.User", related_name="questions", on_delete=models.CASCADE)
    hole = models.ForeignKey(Hole, related_name="questions", on_delete=models.CASCADE)
    question = models.TextField(blank=True, default="")
    is_voice = models.BooleanField(default=False)
    is_answered = models.BooleanField(default=False)
