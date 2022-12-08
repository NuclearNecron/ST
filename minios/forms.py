from django import forms
from minios.models import Document

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('document', )


class MyDocumentForm(forms.Form):
    doc = forms.FileField(
        label='Select a file',
    )