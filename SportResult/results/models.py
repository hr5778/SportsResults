from django.db import models


# Create your models here.
class Sport(models.Model):

    def __str__(self):
        return self.name

    name = models.CharField(max_length=200)


class SportLeague(models.Model):

    def __str__(self):
        return self.name

    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=200)

