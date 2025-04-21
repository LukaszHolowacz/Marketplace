from rest_framework.exceptions import PermissionDenied

class ActiveUserVerifier:
    def verify(self, user):
        if not user.is_active:
            raise PermissionDenied("Twoje konto jest zablokowane.")