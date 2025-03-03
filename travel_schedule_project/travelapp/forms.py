from django import forms
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import AuthenticationForm
from travelapp.models import User

class UserLoginForm(AuthenticationForm):
    email = forms.EmailField(label='メールアドレス')
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput())

class RegistAccountForm(forms.ModelForm):
    username = forms.CharField(label='名前(ユーザーID/変更不可)')
    email = forms.EmailField(label='メールアドレス')
    password = forms.CharField(label= 'パスワード',widget=forms.PasswordInput())
    confirm_password = forms.CharField(label='パスワード再入力', widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username','email','password']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # パスワードをハッシュ化
        if commit:
            user.save()
        return user

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        # パスワードと再入力されたパスワードが一致するかを確認
        if password != confirm_password:
            raise forms.ValidationError('パスワードが一致しません。')

        return cleaned_data
