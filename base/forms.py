from django import forms
from django.contrib.auth import get_user_model
from captcha.fields import CaptchaField
 
class UserCreationForm(forms.ModelForm):
    password = forms.CharField()
 
    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password', )
 
    def clean_password(self):
        password = self.cleaned_data.get("password")
        return password
 
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class ContactForm(forms.Form):
    """ お問い合わせページ用フォーム
    """
    name = forms.CharField(max_length=100, label='名前')
    email = forms.EmailField(max_length=100, label='メールアドレス')
    message = forms.CharField(label='メッセージ', widget=forms.Textarea())
    captcha = CaptchaField(label='画像認証')