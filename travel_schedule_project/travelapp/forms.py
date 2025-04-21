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
from django.forms import formset_factory, modelformset_factory
from .models import TouristPlan
from django import forms
from .models import UserReview
import re

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
            raise forms.ValidationError("ユーザーが見つかりません")

        # パスワードを確認
        if not user.check_password(password):
            raise forms.ValidationError("パスワードが間違っています")

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
        choices=[('', '都道府県を選択')] + PREFECTURE_CHOICES,
        widget=forms.Select(attrs={'class': 'select2'})  # 検索機能付きセレクトボックス
    )
    #Djangoのフォームフィールド に HTMLのクラス属性 (class="select2") を追加するもの
    #select2 は Django の標準機能ではなく、Select2 という JavaScript ライブラリのクラス名

    category = forms.ChoiceField(
        required=False,
        choices=[('', 'カテゴリを選択')] + CATEGORY_CHOICES,
        label='カテゴリ',
        initial='',
        error_messages={'invalid_choice': 'カテゴリが無効です。'},
    )

    workingday = forms.MultipleChoiceField(
        choices=WORKINGDAY_CHOICES,
        widget=forms.CheckboxSelectMultiple,  # 複数チェック可能
        required=False
    )
    parking = forms.ChoiceField(
        choices=[('', '駐車場情報を選択')] +PARKING_CHOICES,
        widget=forms.Select  # プルダウン
    )
    opening_at = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        required=False
    )
    closing_at = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        required=False)

    picture = forms.ImageField(
    required=True,
    widget=forms.FileInput(attrs={'class': 'form-control'})
)

    keywords = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'keyword-input'}),
        required=False,
        help_text="最大10個まで。1つの入力欄につき1キーワード。"
    )


    class Meta:
        model = TouristSpot
        fields = ['spot_name', 'prefecture', 'address', 'tel', 'category', 'workingday', 'parking', 
                  'opening_at', 'closing_at', 'picture', 'description', 'offical_url', 'keywords']

    def clean_address(self):
        address = self.cleaned_data['address']
        # 全角数字や全角ハイフン（−）が含まれていたらエラー
        if any(char in address for char in '０１２３４５６７８９−ー'):
            raise forms.ValidationError("住所の番地部分は半角数字と半角ハイフン（-）のみを使用してください。")
        return address



    def clean_picture(self):
        picture = self.cleaned_data.get('picture')
        if not picture:
            raise forms.ValidationError('画像は必須です。')
        return picture   
    
    def clean_workingday(self):
        workingdays = self.cleaned_data.get('workingday')
        if workingdays:
            return [int(day) for day in workingdays]  # 数値のリストに変換
        return []

    def clean(self):
        cleaned_data = super().clean()
        keywords = self.data.getlist('keywords')
        print("Raw keywords:", keywords)

        keywords_list = [kw.strip() for kw in keywords if kw.strip()]
        print("Cleaned keywords_list:", keywords_list)

        if len(keywords_list) == 0:
            raise forms.ValidationError("少なくとも1つのキーワードを入力してください")
        if len(keywords_list) > 10:
            raise forms.ValidationError("キーワードは10個までです")
        
        # 禁止したい記号や句読点のリスト
        forbidden_chars_pattern = r"[。、，．！？!?\(\)\[\]{}<>「」『』【】・…,.]"
        for kw in keywords_list:
            if len(kw) > 30:
                raise forms.ValidationError(f"キーワード '{kw}' は30文字以内で入力してください")
            
            # 句読点（。、）が含まれていたらエラー
            if re.search(forbidden_chars_pattern, kw):
                raise forms.ValidationError(
                f"キーワード '{kw}' に使用できない文字（句読点・記号など）が含まれています"
            )
        if len(set(keywords_list)) != len(keywords_list):
            raise forms.ValidationError("同じキーワードが複数入力されています。重複しないようにしてください")

        cleaned_data['keywords'] = keywords_list
        return cleaned_data


class UserReviewForm(forms.ModelForm):
    stay_time_hours = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(0, 25)],  # 0～24時間
        label="滞在時間（時間）",
        required=True,
        error_messages={
            'required': '滞在時間（時間）を入力してください。',
        },
    )
    stay_time_minutes = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(0, 60, 10)],  # 0～50分（10分刻み）
        label="滞在時間（分）",
        required=True,
        error_messages={
            'required': '滞在時間（分）を入力してください。',
        },
    )

    review_score = forms.IntegerField(widget=forms.HiddenInput(), required=True)

    class Meta:
        model = UserReview
        fields = [
            'review_score', 'review_title',
            'review_description', 'review_price', 'stay_time_hours', 'stay_time_minutes'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:  # インスタンスがある場合
            hours = self.instance.stay_time_min // 60
            minutes = (self.instance.stay_time_min % 60)
            self.fields['stay_time_hours'].initial = hours
            self.fields['stay_time_minutes'].initial = minutes

    def clean(self):
        cleaned_data = super().clean()

        review_score = cleaned_data.get('review_score')
        stay_time_hours = cleaned_data.get('stay_time_hours')
        stay_time_minutes = cleaned_data.get('stay_time_minutes')

        if not review_score:
            raise forms.ValidationError({'review_score': '評価は必須です。'})

        if not stay_time_hours or not stay_time_minutes:
            if not stay_time_hours:
                raise forms.ValidationError({'stay_time_hours': '滞在時間（時間）は必須です。'})
            if not stay_time_minutes:
                raise forms.ValidationError({'stay_time_minutes': '滞在時間（分）は必須です。'})

        # stay_time_hours と stay_time_minutes が正しい値かどうかを確認
        if not stay_time_hours.isdigit() or not stay_time_minutes.isdigit():
            raise forms.ValidationError({
                'stay_time_hours': '滞在時間（時間）は数字で入力してください。',
                'stay_time_minutes': '滞在時間（分）は数字で入力してください。',
            })

        stay_time_hours = int(stay_time_hours)
        stay_time_minutes = int(stay_time_minutes)

        # 滞在時間が0より大きいことを確認
        if stay_time_hours < 0 or stay_time_minutes < 0:
            raise forms.ValidationError({
                'stay_time_hours': '滞在時間（時間）は0以上の値を設定してください。',
                'stay_time_minutes': '滞在時間（分）は0以上の値を設定してください。',
            })

        # stay_time_min を計算
        stay_time_min = stay_time_hours * 60 + stay_time_minutes

        if stay_time_min <= 0:
            raise forms.ValidationError({
                'stay_time_hours': '滞在時間は0以上の値を設定してください。',
            })
        cleaned_data['stay_time_min'] = stay_time_min

        return cleaned_data



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
    
    def save(self, commit=True):
        tourist_plan = super().save(commit=False)
        if commit:
            tourist_plan.save() 
            for spot_form in self.TouristSpotFormSet(self.data):
                if spot_form.is_valid():
                    spot = spot_form.save(commit=False)
                    spot.tourist_plan = tourist_plan
                    spot.save()
        return tourist_plan


class TouristPlanSpotForm(forms.ModelForm):
    class Meta:
        model = TouristPlan_Spot
        fields = ['tourist_spot', 'visit_date', 'order']
        # 必要に応じてウィジェットなども指定できます
        widgets = {
            'visit_date': forms.DateInput(attrs={'type': 'date'}),
        }

# 既存のスポット群を編集するので、extra=0 としてフォームセットを作成
TouristPlanSpotFormSet = modelformset_factory(
    TouristPlan_Spot,
    form=TouristPlanSpotForm,
    extra=0,
    can_delete=True  # 削除も行えるようにする場合
)
