# from django import forms
# from .models import Order

# class OrderForm(forms.ModelForm):
#     class Meta:
#         model = Order
#         fields = ['payment_method']

from django import forms
from .models import Members
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class RegisterForm(forms.Form):
    name = forms.CharField(max_length=10)  
    nickname = forms.CharField(max_length=10)  # 暱稱
    idNumber = forms.CharField(max_length=10)
    birth = forms.DateField()
    phone = forms.CharField(max_length=10)
    mail = forms.EmailField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput())
    confirmPassword = forms.CharField(widget=forms.PasswordInput())
    
    # class Meta:
    #     model = Members
    #     fields = ['name', 'idNumber', 'birth', 'phone', 'mail', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirmPassword= cleaned_data.get("confirmPassword")

        if password and confirmPassword and password != confirmPassword:            
            raise ValidationError("密碼與確認密碼不一致")
        
        mail = cleaned_data.get("mail")
        idNumber = cleaned_data.get("idNumber")
        nickname = cleaned_data.get("nickname")
        
        if Members.objects.filter(idNumber=idNumber).exists():            
            raise ValidationError("此身分證已被註冊")
        
        if User.objects.filter(email=mail).exists():            
            raise ValidationError("此信箱已被註冊")
    
        if User.objects.filter(username=nickname).exists():            
            raise ValidationError("使用者名稱已被使用")
        return cleaned_data

 

class LoginForm(forms.Form):
    idNumber = forms.CharField(label='身分證字號', max_length=10)
    password = forms.CharField(label='密碼', widget=forms.PasswordInput)


class SetPasswordForm(forms.Form):
    newPassword = forms.CharField(label="新的密碼",widget=forms.PasswordInput())
    confirmPassword = forms.CharField(label="再次確認密碼",widget=forms.PasswordInput())
    
    def clean(self):
        cleaned_data = super().clean()
        newPassword = cleaned_data.get("newPassword")
        ConfirmPassword = cleaned_data.get("confirmPassword")
        if newPassword and ConfirmPassword and newPassword != ConfirmPassword:            
            raise ValidationError("新的密碼與再次確認密碼不同")
        
        return cleaned_data