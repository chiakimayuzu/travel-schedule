from django import forms
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import AuthenticationForm
from travelapp.models import User
from django.core.validators import MinLengthValidator
from django.contrib.auth.forms import PasswordChangeForm as AuthPasswordChangeForm
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from django import forms
from .models import TouristSpot, TouristSpotKeyword, Keyword, PREFECTURES, CATEGORY_CHOICES, WORKINGDAY_CHOICES, PARKING_CHOICES

class UserLoginForm(forms.Form):
    email = forms.EmailField(label='メールアドレス', widget=forms.TextInput(attrs={'placeholder': '例:xxx@example.com'}))
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput(attrs={'placeholder': '英数字8桁以上で入力してください'}))

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        try:
            # メールアドレスを使ってユーザーを取得
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError("ユーザーが見つかりません。")

        # パスワードを確認
        if not user.check_password(password):
            raise ValidationError("パスワードが間違っています。")

        self.user = user  # 認証されたユーザーをフォームにセット
        return cleaned_data     
    
class RegistAccountForm(UserCreationForm):
    email = forms.EmailField(max_length=50, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)  # 一旦DBに保存しない
        user.email = self.cleaned_data['email']  # フォームからemailを取得
        user.username = self.cleaned_data['username']  # フォームからusernameを取得
        if commit:
            user.save()  # 明示的に保存
        return user


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
    
class TouristSpotForm(forms.ModelForm):
    prefecture = forms.ChoiceField(
        choices=PREFECTURES,
        widget=forms.Select(attrs={'class': 'select2'})  # 検索機能付きセレクトボックス
    )
    #Djangoのフォームフィールド に HTMLのクラス属性 (class="select2") を追加するもの
    #select2 は Django の標準機能ではなく、Select2 という JavaScript ライブラリのクラス名
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        widget=forms.Select(attrs={'class': 'select2'})  # 検索機能付きセレクトボックス
    )
    workingday = forms.MultipleChoiceField(
        choices=WORKINGDAY_CHOICES,
        widget=forms.CheckboxSelectMultiple,  # 複数チェック可能
        required=False
    )
    parking = forms.ChoiceField(
        choices=PARKING_CHOICES,
        widget=forms.Select  # プルダウン
    )
    picture = forms.ImageField(required=False)
    
    keywords = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '例: 海, 山, 温泉'}),  # ★自由入力可能なテキストボックスに変更
        required=True,  # ★1つ以上のキーワードが必須
        help_text="カンマ（,）区切りで複数のキーワードを入力できます"
    )


    class Meta:
        model = TouristSpot
        fields = ['spot_name', 'prefecture', 'address', 'tel', 'category', 'workingday', 'parking', 
                  'opening_at', 'closing_at', 'picture', 'description', 'offical_url', 'latitude', 'longitude', 'keywords']


    def clean_keywords(self):
        keywords_text = self.cleaned_data.get('keywords')
        keywords_list = [kw.strip() for kw in keywords_text.split(',') if kw.strip()]  # ★カンマ区切りでリスト化
        if len(keywords_list) == 0:
            raise forms.ValidationError("少なくとも1つのキーワードを入力してください")  # ★1つ以上のキーワードが必要
        if len(keywords_list) > 10:
            raise forms.ValidationError("1つの観光地に登録できるキーワードは10個までです")  # ★最大10個まで
        return keywords_list  # ★cleaned_data にリストとして保存
