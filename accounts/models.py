from django.db import models
from django.contrib.auth.models import AbstractUser
from mountains.models import Mountain, Course


class User(AbstractUser):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=256)
    nickname = models.CharField(max_length=20, unique=True, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    profile_img = models.ImageField(blank=True, null=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    followings = models.ManyToManyField('self', symmetrical=False, related_name='followers')
    message = models.CharField(max_length=200, blank=True)
    kakao_user_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    naver_user_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    visited_courses = models.ManyToManyField(Course, through='VisitedCourse', related_name='visitors', blank=True)
    level = models.IntegerField(default=1)


class VisitedCourse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    mountain_name = models.CharField(max_length=50)
    mountain_id = models.IntegerField()

    def __str__(self):
        return self.mountain_name

    def save(self, *args, **kwargs):
        self.mountain_name = self.course.mntn_name
        self.mountain_id = self.course.mntn_name.id
        super().save(*args, **kwargs)