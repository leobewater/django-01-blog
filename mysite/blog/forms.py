from django import forms

from .models import Comment


# using Form
class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    # override default widget
    comments = forms.CharField(required=False, widget=forms.Textarea)


# using ModelForm
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']
