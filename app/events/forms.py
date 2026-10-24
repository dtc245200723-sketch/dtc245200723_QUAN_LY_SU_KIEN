from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Event


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(label='Họ và tên', max_length=150, required=False)
    email = forms.EmailField(label='Địa chỉ email', required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email', 'password1', 'password2')
        labels = {
            'username': 'Tên đăng nhập',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Mật khẩu'
        self.fields['password2'].label = 'Nhập lại mật khẩu'


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'event_code',
            'title',
            'description',
            'category',
            'event_date',
            'end_date',
            'registration_deadline',
            'location',
            'capacity',
        ]
        labels = {
            'event_code': 'Mã sự kiện (để trống để tự tạo)',
            'title': 'Tên sự kiện',
            'description': 'Mô tả',
            'category': 'Thể loại',
            'event_date': 'Thời gian bắt đầu',
            'end_date': 'Thời gian kết thúc',
            'registration_deadline': 'Hạn đăng ký',
            'location': 'Địa điểm',
            'capacity': 'Sức chứa tối đa',
        }
        widgets = {
            'event_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'registration_deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')


class RegistrationForm(forms.Form):
    attendee_name = forms.CharField(label='Họ và tên', max_length=200)
    email = forms.EmailField(label='Email', disabled=True, required=False)
    phone = forms.CharField(label='Số điện thoại', max_length=30, required=False)

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].initial = getattr(user, 'email', '')
        if user and not self.is_bound:
            self.fields['attendee_name'].initial = user.get_full_name() or user.get_username()
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')


class AccountSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Tên',
            'last_name': 'Họ',
            'email': 'Email',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
