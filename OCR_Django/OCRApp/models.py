
from django.db import models

#


class ImageFile(models.Model):

    files = models.FileField(upload_to="Files/")
    uploaded_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.pk)
