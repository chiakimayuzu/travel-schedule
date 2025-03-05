from django import forms
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import AuthenticationForm
from travelapp.models import User
from django.core.validators import MinLengthValidator
from django.contrib.auth.forms import PasswordChangeForm as AuthPasswordChangeForm
from django.core.exceptions import ValidationError



class UserLoginForm(AuthenticationForm):
    email = forms.EmailField(label='メールアドレス',widget=forms.TextInput(attrs={'placeholder': '例:xxx@example.com'}))
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput(attrs={'placeholder': '英数字8桁以上で入力してください'}))

class RegistAccountForm(forms.ModelForm):
    username = forms.CharField(
                label='名前(ユーザーID/変更不可)',
                widget=forms.TextInput(attrs={'placeholder': '例:travelchan1234'}))
    email = forms.EmailField(
                label='メールアドレス',
                widget=forms.TextInput(attrs={'placeholder': '例:xxx@example.com'}))
    password = forms.CharField(
                label='パスワード',
                widget=forms.PasswordInput(attrs={'placeholder': '英数字8桁以上で入力してください'}),
                validators=[MinLengthValidator(8)])
    confirm_password = forms.CharField(
                label='パスワード再入力',
                widget=forms.PasswordInput(attrs={'placeholder': '英数字8桁以上で入力してください'}))

    class Meta:
        model = User
        fields = ['username','email','password','confirm_password']
    
    def save(self, commit=True):
        user = super().save(commit=True)  # 保存処理を1回で済ませる
        return user

        
    # def save(self, commit=True):
    #     user = super().save(commit=False)
    #     user.set_password(self.cleaned_data['password'])  # パスワードをハッシュ化
    #     if commit:
    #         user.save()
    #     return user

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        # パスワードと再入力されたパスワードが一致するかを確認
        if password != confirm_password:
            raise forms.ValidationError('パスワードが一致しません。')
        
        # ユーザー名の重複をチェック（ユーザー名がすでに登録されていないか）
        username = cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('このユーザー名は既に登録されています。')
        
         # メールアドレスの重複をチェック（メールアドレスがすでに登録されていないか）
        email = cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('このメールアドレスは既に登録されています。')
        
        return cleaned_data

class ChangeEmailForm(forms.Form):
    current_email = forms.EmailField(
        label='現在のメールアドレス',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '現在のメールアドレス'}),
    )
    new_email = forms.EmailField(
        label='新しいメールアドレス',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '新しいメールアドレス'}),
    )
    confirm_email = forms.EmailField(
        label='メールアドレス再入力',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'メールアドレス再入力'}),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_email(self):
        current_email = self.cleaned_data.get('current_email')
        if current_email != self.user.email:
            raise ValidationError("現在のメールアドレスが一致しません。")
        return current_email

    def clean(self):
        cleaned_data = super().clean()
        new_email = cleaned_data.get("new_email")
        confirm_email = cleaned_data.get("confirm_email")

        if new_email != confirm_email:
            raise ValidationError("新しいメールアドレスが一致しません。")
        return cleaned_data

class PasswordChangeForm(AuthPasswordChangeForm):
    old_password = forms.CharField(
        label='現在のパスワード',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),)
    new_password1 = forms.CharField(
        label='新しいパスワード',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),)
    new_password2 = forms.CharField(
        label='新しいパスワード（再入力）',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(user, *args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise ValidationError("現在のパスワードが一致しません。")
        return old_password