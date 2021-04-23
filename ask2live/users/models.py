from django.db import models
from django.contrib.auth.models import AbstractUser
from holes import models as hole_models
from core import models as core_model
# token authentication
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.utils.translation import ugettext_lazy as _


from django.contrib.auth.base_user import BaseUserManager

def nameFile(instance, filename):
    return '/'.join(['profile_images',filename])


# Create your models here.
class User(AbstractUser):
    """ user model attribute"""
    profile_image = models.ImageField(blank=True, max_length=255, 
        upload_to = nameFile
    )
    bio = models.TextField(default="", blank=True)
    work_company = models.CharField(max_length=100,default="",blank=True)
    work_field = models.CharField(max_length=100, default="", blank=True) # 일하는 분야
    uid = models.BigIntegerField(blank=True, default=0)

    def get_photo_url(self):
        profile_img = self.profile_image
        return profile_img.url

# token authentication
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender,instance=None, created=False, **kwargs):
    if created:
        token = Token.objects.create(user=instance) # 유저가 생성되면 토큰이 만들어짐.


class UserFollowing(core_model.AbstractTimeStamp):
    user_id = models.ForeignKey(User,related_name="following", on_delete=models.CASCADE) # 내가 following
    following_user_id = models.ForeignKey(User, related_name="followers", on_delete=models.CASCADE) # 나를 following
    created = models.DateTimeField(auto_now_add=True, db_index=True) # db_index는?

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user_id', 'following_user_id'], name="unique_followers")
        ]
