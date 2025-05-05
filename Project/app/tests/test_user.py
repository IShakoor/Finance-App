from django.test import TestCase
from app.models import CustomUser
from app.tests.factories import UserFactory

class UserModelTests(TestCase):

    # test valid user creation
    def test_create_valid_user(self):
        user = UserFactory(username="regularuser", email="regularuser@example.com")
        self.assertEqual(user.username, "regularuser")
        self.assertEqual(user.email, "regularuser@example.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    # test default values for user creations
    def test_user_default(self):
        user = UserFactory()
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    # test invalid email
    def test_invalid_email(self):
        with self.assertRaises(ValueError) as context:
            CustomUser.objects.create_user(username="testuser", email="notanemail", password="password123")
        self.assertEqual(str(context.exception), "Invalid email format")

    # test user creation without email
    def test_user_creation_without_email(self):
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(username="testuser", email=None, password="password123")

    # test password hash
    def test_password_hashing(self):
        user = UserFactory(password="securepassword")
        self.assertNotEqual(user.password, "securepassword")
        self.assertTrue(user.check_password("securepassword"))

    # test string method
    def test_user_string(self):
        user = UserFactory(email="testingemail@example.net")
        self.assertEqual(str(user), "testingemail@example.net")

    # test superuser creation
    def test_create_superuser(self):
        superuser = UserFactory(
            username="adminuser",
            email="adminuser@example.com",
            is_staff=True,
            is_superuser=True,
            is_active=True,
            is_verified=False,
        )
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertFalse(superuser.is_verified)

    # test invalid superuser creation
    def test_create_superuser_invalid(self):
        with self.assertRaises(ValueError) as context:
            CustomUser.objects.create_superuser(
                username="adminuser",
                email="admin@example.com",
                password=None,
            )
        self.assertEqual(str(context.exception), "Superuser must have a password.")

    # test access token (saving)
    def test_plaid_access_token(self):
        user = UserFactory(plaid_access_token="sample_token")
        self.assertEqual(user.plaid_access_token, "sample_token")
        user.plaid_access_token = None
        user.save()
        self.assertIsNone(user.plaid_access_token)

    # test required fields
    def test_required_fields(self):
        self.assertEqual(CustomUser.REQUIRED_FIELDS, ['username'])
        self.assertEqual(CustomUser.USERNAME_FIELD, 'email')

    # test user joined date
    def test_date_joined_auto_now(self):
        user = UserFactory()
        self.assertIsNotNone(user.date_joined)

    # testing is_verified (should be false upon acc creation)
    def test_is_verified_default(self):
        user = UserFactory()
        self.assertTrue(user.is_verified)
        
        user.is_verified = False
        user.save()
        refreshed_user = CustomUser.objects.get(pk=user.pk)
        self.assertFalse(refreshed_user.is_verified)  