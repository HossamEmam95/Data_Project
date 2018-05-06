from django import forms
from django.contrib.auth import authenticate

from .models import User, Post, Comment


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self, *args, **kwargs):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']

        user_qs = User.objects.filter(username=username)
        user = user_qs.first()
        if username and password:
            if not user:
                raise forms.ValidationError("This user does not exist")
            if not user.check_password(password):
                raise forms.ValidationError("Incorrect password")
            if not user.is_active:
                raise forms.ValidationError("This user is not longer active.")

        return super(LoginForm, self).clean(*args, **kwargs)


class RegisterForm(forms.ModelForm):
    email2 = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username',
                  'password',
                  'email',
                  'email2',
                  'first_name',
                  'last_name',
                  'birthday',
                  'work',
                  'address',
                  'phone_number',
                  'gender'
                  )

    def clean(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.get(username=username)
            raise forms.ValidationError("username with this name is found, change it")
        except User.DoesNotExist:
            pass

        if self.cleaned_data['email2'] != self.cleaned_data['email']:
            raise forms.ValidationError("The email doesn't match")
        return super(RegisterForm, self).clean()


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('body',)

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['body'].label = ' '


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)
        widgets = {
            'body': forms.Textarea(attrs={'rows': 1, 'cols': 50 }),
        }

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['body'].label = ' '

