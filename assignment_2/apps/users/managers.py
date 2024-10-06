from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username: str, password: str):
        if not username:
            raise ValueError('The username field must be set')
        user = self.model(username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        user = self.create_user(
            username=username,
            password=password
        )
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

    def get_queryset(self):
        return super().get_queryset().select_related("blog_user")
