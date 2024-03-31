from django.db import models

class articles(models.Model):
    source = models.CharField(max_length = 50)
    author = models.CharField(max_length = 50, null = True)
    title = models.CharField(max_length = 200, unique=True)
    description = models.CharField(max_length = 200, unique=True)
    url = models.CharField(max_length = 50)
    image_url = models.CharField(max_length = 50, null = True)
    publish_date = models.DateTimeField()
    content = models.TextField(null = True, unique=True)
    category = models.CharField(max_length = 50)
    feature_vector = models.TextField(default = '[]')