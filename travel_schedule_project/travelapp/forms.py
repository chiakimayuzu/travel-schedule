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
from .models import TouristPlan_Spot, TouristSpot, TouristSpotKeyword, Keyword, PREFECTURE_CHOICES, CATEGORY_CHOICES, WORKINGDAY_CHOICES, PARKING_CHOICES, UserReview
from .models import TouristPlan
from django.forms import formset_factory
from .models import TouristPlan
from django import forms
from .models import UserReview


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
    email = forms.EmailField(
        max_length=50,
        required=True,
        widget=forms.EmailInput(attrs={"placeholder": "例:xxx@example.com"})
    )
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"placeholder": "travelschedulesan"}),
        help_text="クチコミ投稿時などにこのユーザー名が表示されます"
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "英数字8桁以上で入力してください"}),
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "英数字8桁以上で入力してください"}),
        help_text="確認のため、同じパスワードを入力してください。"
    )
    
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
        choices=PREFECTURE_CHOICES,
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
    opening_at = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        required=False
    )
    closing_at = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        required=False)

    picture = forms.ImageField(required=False)

    keywords = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '例: 海, 山, 温泉'}),  # ★自由入力可能なテキストボックスに変更
        required=True,  # ★1つ以上のキーワードが必須
        help_text="カンマ（,）区切りで複数のキーワードを入力できます / 1つの観光地に登録できるキーワードは10個までです"
    )


    class Meta:
        model = TouristSpot
        fields = ['spot_name', 'prefecture', 'address', 'tel', 'category', 'workingday', 'parking', 
                  'opening_at', 'closing_at', 'picture', 'description', 'offical_url', 'keywords']

    
    def clean_workingday(self):
        workingdays = self.cleaned_data.get('workingday')
        if workingdays:
            return [int(day) for day in workingdays]  # 数値のリストに変換
        return []

    def clean_keywords(self):
        keywords_text = self.cleaned_data.get('keywords')
        keywords_list = [kw.strip() for kw in keywords_text.split(',') if kw.strip()]  # ★カンマ区切りでリスト化
        if len(keywords_list) == 0:
            raise forms.ValidationError("少なくとも1つのキーワードを入力してください")  # ★1つ以上のキーワードが必要
        if len(keywords_list) > 10:
            raise forms.ValidationError("1つの観光地に登録できるキーワードは10個までです")  # ★最大10個まで
        return keywords_list  # ★cleaned_data にリストとして保存



class UserReviewForm(forms.ModelForm):
    stay_time_hours = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(0, 25)],  # 0～24時間
        label="滞在時間（時間）"
    )
    stay_time_minutes = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(0, 60, 10)],  # 0～50分（10分刻み）
        label="滞在時間（分）"
    )
    
    review_score = forms.IntegerField(widget=forms.HiddenInput())

    class Meta:
        model = UserReview
        fields = [
            'review_score', 'review_title',
            'review_description', 'review_price', 'stay_time_hours', 'stay_time_minutes'
        ]

    def save(self, commit=True):
        instance = super().save(commit=False)
        hours = int(self.cleaned_data.get('stay_time_hours', 0))
        minutes = int(self.cleaned_data.get('stay_time_minutes', 0))
        instance.stay_time_min = hours * 60 + minutes
        if commit:
            instance.save()
        return instance


class TouristSpotSearchForm(forms.Form):
    query = forms.CharField(
        required=False, 
        label='検索キーワード', 
        widget=forms.TextInput(attrs={'placeholder': 'スポット名、キーワード、説明、住所で検索'})
    )
    
    category = forms.ChoiceField(
        required=False,
        choices=[('', 'カテゴリを選択')] + CATEGORY_CHOICES,
        label='カテゴリ',
        initial='',
        error_messages={'invalid_choice': 'カテゴリが無効です。'},
    )

    order_by = forms.ChoiceField(
        choices=[
            ('review_score_average', '評価がいい順'),
            ('created_at', '新しい順'),
            ('-created_at', '古い順'),
        ], 
        initial='review_score_average',
        label='並び順'
    )
    
    # 日付を選択するためのフィールド追加
    visit_date = forms.DateField(
        widget=forms.SelectDateWidget(years=range(2025, 2030)), 
        required=True,
        label='訪問日'
    )



class TouristPlanForm(forms.ModelForm):
    # Start date と end date に基づいて訪問日を動的に生成するフィールドを作成
    start_date = forms.DateField(widget=forms.SelectDateWidget(years=range(2025, 2030)), required=True)
    end_date = forms.DateField(widget=forms.SelectDateWidget(years=range(2025, 2030)), required=True)

    class Meta:
        model = TouristPlan
        fields = ['touristplan_name', 'start_date', 'end_date']

    # モーダルで選択する観光地のフォームセット
    TouristSpotFormSet = formset_factory(TouristPlan_Spot, extra=1)

    # start_date が end_date より後でないことを確認
    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')
        
        if end_date and start_date > end_date:
            raise forms.ValidationError("Start date must be before the end date.")
        
        return start_date

    # end_date が start_date より前でないことを確認
    def clean_end_date(self):
        end_date = self.cleaned_data.get('end_date')
        start_date = self.cleaned_data.get('start_date')

        if start_date and end_date < start_date:
            raise forms.ValidationError("End date must be after the start date.")
        
        return end_date



# class TouristPlanForm(forms.ModelForm):
#     # Start date と end date に基づいて訪問日を動的に生成するフィールドを作成
#     start_date = forms.DateField(widget=forms.SelectDateWidget(years=range(2025, 2030)), required=True)
#     end_date = forms.DateField(widget=forms.SelectDateWidget(years=range(2025, 2030)), required=True)

#     class Meta:
#         model = TouristPlan
#         fields = ['touristplan_name', 'start_date', 'end_date']

#     # モーダルで選択する観光地のフォームセット
#     TouristSpotFormSet = formset_factory(TouristPlan_Spot, extra=1)

#     def clean(self):
#         cleaned_data = super().clean()
#         start_date = cleaned_data.get('start_date')
#         end_date = cleaned_data.get('end_date')
        
#         # start_date と end_date が選択されていることを確認
#         if start_date and end_date and start_date > end_date:
#             raise forms.ValidationError("End date must be after the start date.")
        
#         return cleaned_data