from django.forms import ModelForm
from .models import ImageFile


class ImageForm(ModelForm):
    class Meta:
        model = ImageFile
        fields = '__all__'
