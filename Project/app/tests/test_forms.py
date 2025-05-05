from django.test import Client, TestCase
from django.urls import reverse
from app.tests.factories import UserFactory
from django.contrib.auth.hashers import check_password
from unittest.mock import patch
from app.forms import *

# testing signup form logic
class SignupFormTests(TestCase):

    # test valid signup form
    def test_valid_signup(self):
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'StrongPassword123!',
            'password2': 'StrongPassword123!',
        }
        form = SignupForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertTrue(check_password('StrongPassword123!', user.password))

    # test password mismatch
    def test_signup_password_mismatch(self):
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'StrongPassword123!',
            'password2': 'DifferentPassword456!',
        }
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        
        self.assertIn('password2', form.errors)
        self.assertEqual(form.errors['password2'][0], "The two password fields didn’t match.")

    # testing duplicate emails
    def test_signup_duplicate_email(self):
        UserFactory(email='duplicate@example.com')
        form_data = {
            'username': 'newuser',
            'email': 'duplicate@example.com',
            'password1': 'Password123',
            'password2': 'Password123',
        }
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('This email is already taken. Please use a different email.', form.errors['email'])

    # test duplicate usernames
    def test_duplicate_username(self):
        # Create a user first
        user = UserFactory(username="uniqueuser")
        
        # Create a form with duplicate username
        form_data = {
            'username': 'uniqueuser',
            'email': 'different@example.com',
            'password1': 'password123',
            'password2': 'password123',
            # Include any other required fields
        }
        
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertEqual(form.errors['username'][0], "This username is already taken. Please choose another one.")

    # Test empty fields
    def test_empty_fields(self):
        form_data = {
            'username': '',
            'email': '',
            'password1': '',
            'password2': '',
        }
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('password1', form.errors)
        self.assertIn('password2', form.errors)

    # test invalid email format
    def test_invalid_email_format(self):
        form_data = {
            'username': 'newuser',
            'email': 'not-an-email',
            'password1': 'Password123',
            'password2': 'Password123',
        }
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    # test password too short
    def test_password_too_short(self):
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'Short1!',
            'password2': 'Short1!',
        }
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)
        self.assertEqual(form.errors['password1'][0], "Password must be at least 8 characters long")

    # test password without uppercase
    def test_password_no_uppercase(self):
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'password123!',
            'password2': 'password123!',
        }
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)
        self.assertEqual(form.errors['password1'][0], "Password must contain at least one uppercase letter")

    # test password without number
    def test_password_no_number(self):
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'Password!',
            'password2': 'Password!',
        }
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)
        self.assertEqual(form.errors['password1'][0], "Password must contain at least one number")

    # test password without special character
    def test_password_no_special_char(self):
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'Password123',
            'password2': 'Password123',
        }
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)
        self.assertEqual(form.errors['password1'][0], "Password must contain at least one special character (!@#$%^&*.)")

    # test password same as username
    def test_password_same_as_username(self):
        form_data = {
            'username': 'Password123!',
            'email': 'newuser@example.com',
            'password1': 'Password123!',
            'password2': 'Password123!',
        }
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)
        self.assertEqual(form.errors['password1'][0], "Password cannot be the same as your username.")

    # test password same as email
    def test_password_same_as_email(self):
        form_data = {
            'username': 'newuser',
            'email': 'Password123!@example.com',
            'password1': 'Password123!@example.com', 
            'password2': 'Password123!@example.com',
        }
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)
        self.assertEqual(form.errors['password1'][0], "Password cannot be the same as your email.")

    # test form widget attributes
    def test_form_widget_attributes(self):
        form = SignupForm()
        
        # test placeholders
        self.assertEqual(form.fields['username'].widget.attrs['placeholder'], 'Username')
        self.assertEqual(form.fields['email'].widget.attrs['placeholder'], 'Email Address')
        self.assertEqual(form.fields['password1'].widget.attrs['placeholder'], 'Password')
        self.assertEqual(form.fields['password2'].widget.attrs['placeholder'], 'Confirm Password')
        
        # test CSS classes
        self.assertEqual(form.fields['username'].widget.attrs['class'], 'form-input')
        self.assertEqual(form.fields['email'].widget.attrs['class'], 'form-input')
        self.assertEqual(form.fields['password1'].widget.attrs['class'], 'form-input')
        self.assertEqual(form.fields['password2'].widget.attrs['class'], 'form-input')
        
        # test that labels are empty
        self.assertEqual(form.fields['username'].label, "")
        self.assertEqual(form.fields['email'].label, "")
        self.assertEqual(form.fields['password1'].label, "")
        self.assertEqual(form.fields['password2'].label, "")
        
        # test help text for password
        self.assertIn("at least 8 characters", form.fields['password1'].help_text)
        self.assertIn("at least one capital letter", form.fields['password1'].help_text)
        self.assertIn("at least one number", form.fields['password1'].help_text)
        self.assertIn("at least one special character", form.fields['password1'].help_text)

# testing the login form
class LoginFormTests(TestCase):
    def setUp(self):
        self.test_user = UserFactory(
            email='testuser@example.com',
            username='testuser'
        )
        self.test_user.set_password('Password123!')
        self.test_user.save()

    # simulating a valid login with mocks to bypass encryption
    @patch('app.forms.LoginForm.clean')
    def test_valid_login_with_mock(self, mock_clean):
        mock_clean.return_value = {'email': 'testuser@example.com', 'password': 'Password123!'}
        form = LoginForm(data={
            'email': 'testuser@example.com',
            'password': 'Password123!'
        })

        form.user_cache = self.test_user
        self.assertTrue(form.is_valid())
        self.assertEqual(form.user_cache.email, 'testuser@example.com')

    # login with invalid email
    def test_invalid_email(self):
        form_data = {
            'email': 'nonexistent@example.com',
            'password': 'Password123!'
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
    
    # login with invalid password
    def test_invalid_password(self):
        form_data = {
            'email': 'testuser@example.com',
            'password': 'WrongPassword123!'
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)

    # test empty email
    def test_empty_email(self):
        form_data = {
            'email': '',
            'password': 'Password123!'
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    # test empty password
    def test_empty_password(self):
        form_data = {
            'email': 'testuser@example.com',
            'password': ''
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)
    
    # test form attributes
    def test_form_widget_attributes(self):
        form = LoginForm()
        
        # placeholders
        self.assertEqual(form.fields['email'].widget.attrs['placeholder'], 'Email Address')
        self.assertEqual(form.fields['password'].widget.attrs['placeholder'], 'Password')
        
        # CSS
        self.assertEqual(form.fields['email'].widget.attrs['class'], 'form-input')
        self.assertEqual(form.fields['password'].widget.attrs['class'], 'form-input')


# testing password reset form
class PasswordResetFormTests(TestCase):
    def setUp(self):
        self.user = UserFactory()

    # test valid email
    def test_valid_password_reset(self):
        form_data = {'email': self.user.email}
        form = PasswordResetForm(data=form_data)
        self.assertTrue(form.is_valid())

    # test unknown email
    def test_password_reset_unknown_email(self):
        form_data = {'email': 'unknown@example.com'}
        form = PasswordResetForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    # test empty email
    def test_empty_email(self):
        form_data = {'email': ''}
        form = PasswordResetForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    # test invalid email
    def test_invalid_email_format(self):
        form_data = {'email': 'not-an-email'}
        form = PasswordResetForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        
    def test_form_widget_attributes(self):
        form = PasswordResetForm()
        # test placeholder
        self.assertEqual(form.fields['email'].widget.attrs['placeholder'], 'Email Address')
        # test CSS
        self.assertEqual(form.fields['email'].widget.attrs['class'], 'form-input')
        # test label is empty
        self.assertEqual(form.fields['email'].label, "")
        # test max length
        self.assertEqual(form.fields['email'].max_length, 254)
        
    # testing different data passwed into form
    def test_form_initialization_with_different_data_types(self):
        form = PasswordResetForm(data=None)
        self.assertFalse(form.is_valid())
        
        form = PasswordResetForm(data={})
        self.assertFalse(form.is_valid())
        
    # test normalised email
    def test_email_normalization(self):
        form_data = {'email': 'Test.User@Example.COM'}
        form = PasswordResetForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    # test extra fields
    def test_form_with_extra_fields(self):
        form_data = {
            'email': self.user.email,
            'extra_field': 'should be ignored'
        }
        form = PasswordResetForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertNotIn('extra_field', form.cleaned_data)
        
    # test required field
    def test_email_required(self):
        form = PasswordResetForm()
        self.assertTrue(form.fields['email'].required)


# testing password reset confirmation
class PasswordResetConfirmFormTests(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.url = reverse('password_reset_confirm', kwargs={'user_id': self.user.id})
        self.client = Client()

    # test valid password
    def test_form_valid_password(self):
        form_data = {'password1': 'ValidP@ss123', 'password2': 'ValidP@ss123'}
        form = PasswordResetConfirmForm(data=form_data)
        self.assertTrue(form.is_valid())

    # test short password
    def test_password_too_short(self):
        form_data = {'password1': 'Short1!', 'password2': 'Short1!'}
        form = PasswordResetConfirmForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Password must be at least 8 characters long', form.errors['password1'])

    # test password no caps
    def test_password_no_uppercase(self):
        form_data = {'password1': 'nouppercase1!', 'password2': 'nouppercase1!'}
        form = PasswordResetConfirmForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Password must contain at least one uppercase letter', form.errors['password1'])

    # test password no number
    def test_password_no_number(self):
        form_data = {'password1': 'NoNumber!', 'password2': 'NoNumber!'}
        form = PasswordResetConfirmForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Password must contain at least one number', form.errors['password1'])

    # test password no char
    def test_password_no_special_char(self):
        form_data = {'password1': 'NoSpecial123', 'password2': 'NoSpecial123'}
        form = PasswordResetConfirmForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Password must contain at least one special character (!@#$%^&*.)', form.errors['password1'])

    # test password mismatch
    def test_passwords_dont_match(self):
        form_data = {'password1': 'ValidP@ss123', 'password2': 'DifferentP@ss123'}
        form = PasswordResetConfirmForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Passwords do not match.', form.errors['password1'])

    # no password 2
    def test_missing_password2(self):
        form_data = {'password1': 'ValidP@ss123'}
        form = PasswordResetConfirmForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    # test view fetching
    def test_view_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/password_reset_confirm.html')
        self.assertIsInstance(response.context['form'], PasswordResetConfirmForm)

    # test the post form
    def test_view_post_valid(self):
        old_password_hash = self.user.password
        response = self.client.post(self.url, {
            'password1': 'NewValidP@ss123',
            'password2': 'NewValidP@ss123'
        }, follow=True)
        
        self.user.refresh_from_db()
        self.assertNotEqual(old_password_hash, self.user.password)
        self.assertRedirects(response, reverse('login'))
        self.assertContains(response, "Your password has been reset successfully")

    # test invalid post
    def test_view_post_invalid(self):
        old_password_hash = self.user.password
        response = self.client.post(self.url, {
            'password1': 'short',
            'password2': 'short'
        })
        
        self.user.refresh_from_db()
        self.assertEqual(old_password_hash, self.user.password)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/password_reset_confirm.html')
        self.assertFalse(response.context['form'].is_valid())

    # test invalid user
    def test_view_invalid_user_id(self):
        invalid_url = reverse('password_reset_confirm', kwargs={'user_id': 99999})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)