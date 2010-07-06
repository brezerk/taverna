from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class OpenIDBackend:
    """Return User record if username + (some test) is valid.
    Return None if no match.
    """

    def authenticate(self, username=None, password=None, request=None):
        try:
            if password:
                user = User.objects.get(username=username, password=password)
            else:
                user = User.objects.get(username=username)
                if user.is_staff or user.is_superuser:
                    return None
            # plus any other test of User/UserProfile, etc.
            return user # indicates success
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

