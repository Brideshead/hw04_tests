from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class CreationForm(UserCreationForm):
    """
    Класс для формы регистрации.
    """

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
        labels = {
            'username': 'псевдоним',
        }
        help_texts = {
            'first_name': 'имя',
            'last_name': 'фамилия',
            'username': 'имя',
            'email': 'почта',
        }
