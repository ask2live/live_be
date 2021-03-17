from django.db import models
from django.db.models import IntegerField, Model
from users import models as user_models
from core import models as core_model
from django_mysql.models import ListTextField
from django.db.models import Q
# Create your models here.

class HoleQuerySet(models.QuerySet):
    def notStart(self):
        return self.filter(status="not_start")
    
    def doing(self):
        return self.filter(status="doing")
    
    def done(self):
        return self.filter(status="done")
    
    def search(self, query=None):
        queryset = self
        if query is not None:
            or_lookup = (Q(title__icontains=query) |
                        Q(subtitle__icontains=query) |
                        Q(description__icontains=query)
                        )
            queryset = queryset.filter(or_lookup).distinct()
        return queryset

class HoleManager(models.Manager):

    def get_queryset(self):
        return HoleQuerySet(self.model, using=self._db)

    def notStart(self):
        return self.get_queryset().notStart()
    
    def doing(self):
        return self.get_queryset().doing()
    
    def done(self):
        return self.get_queryset.done()
    
    def search(self, query=None):
        return self.get_queryset().search(query=query)


class Hole(core_model.AbstractTimeStamp):
    STATUS_NOTSTART = "not_start"
    STATUS_DOING = "doing"
    STATUS_DONE = "done"
    STATUS_CHOICES = (
        (STATUS_NOTSTART, "Not_Start"),
        (STATUS_DOING, "Doing"),
        (STATUS_DONE, "Done"),
    )
    title           = models.CharField(max_length=200)    # 세션 제목
    subtitle        = models.CharField(max_length=400) # 세션 부제
    description     = models.TextField()            # 세션 설명
    reserve_date    = models.DateTimeField(blank=True, null=True) # 세션 시작하는 날짜
    finish_date     = models.DateTimeField(blank=True, null = True) # 세션이 종료되는 날짜    

    status          = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_NOTSTART)
    rating          = models.IntegerField(blank=True, default=0)
    # ====================== 나중에 models.ForeignKey로 변경 ======================
    host            = models.ForeignKey("users.User", related_name="hole",blank=True, on_delete=models.CASCADE)

    objects = HoleManager()
    
    def __str__(self):
        return self.title


class LiveHole(core_model.AbstractTimeStamp):
    hole = models.ForeignKey(Hole,related_name="liveholes", on_delete=models.CASCADE, blank=True)
    participants = models.ManyToManyField("users.User", related_name="liveholes",blank=True) #null이 들어가도 되는건가?
    
    def __str__(self):
        usernames = []
        all_member = self.participants.all()
        for member in all_member:
            usernames.append(member.username)
        return ", ".join(usernames)


class Question(core_model.AbstractTimeStamp):
    user = models.ForeignKey("users.User", related_name="questions", on_delete=models.CASCADE)
    hole = models.ForeignKey(Hole, related_name="questions", on_delete=models.CASCADE)
    question = models.TextField(blank=True, default="")
