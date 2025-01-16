from django.db import models

class OpenHouseEvent(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    details_url = models.URLField()

    def __str__(self):
        return self.title
