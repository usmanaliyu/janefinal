from django import forms


class BlogCommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': 'Comment',
        'style': 'resize:none',
        'rows': 16,
        'class': 'form-control'
    }))
    
