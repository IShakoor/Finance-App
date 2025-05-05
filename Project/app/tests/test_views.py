from app.tests.factories import UserFactory
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from app.views import *
from django.conf import settings
from app.forms import *
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.messages import get_messages
from django.core import mail
from unittest.mock import patch, MagicMock
from app.models.user import CustomUser

# testing the home view
class HomeViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.home_url = reverse('home')
        self.login_url = reverse('login')
        self.factory = RequestFactory()

    # test page redirects to login if user is not authenticated
    def test_login_required(self):
        response = self.client.get(self.home_url)
        login_url = getattr(settings, 'LOGIN_URL', '/accounts/login/')
        expected_redirect_url = f'{login_url}?next={self.home_url}'
        self.assertRedirects(
            response, 
            expected_redirect_url, 
            fetch_redirect_response=False
        )

    # test authenticated users can access
    def test_authenticated_access(self):
        self.client.force_login(self.user)
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/home.html')

    # test that view provides correct context
    def test_context_data(self):
        self.client.force_login(self.user)
        response = self.client.get(self.home_url)
        self.assertEqual(response.context['user'], self.user)

    # test view request
    def test_direct_view_function(self):
        request = self.factory.get(self.home_url)
        request.user = self.user
        response = home_view(request)
        self.assertEqual(response.status_code, 200)
    
    # test anonymous users are redicrected to login
    def test_anonymous_user_redirect(self):
        request = self.factory.get(self.home_url)
        request.user = AnonymousUser()
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        
        response = home_view(request)
        self.assertEqual(response.status_code, 302)
        login_url = getattr(settings, 'LOGIN_URL', '/accounts/login/')
        self.assertTrue(response.url.startswith(login_url))

    # test that view only accepts GET requests
    def test_http_methods(self):
        self.client.force_login(self.user)
        get_response = self.client.get(self.home_url)
        self.assertEqual(get_response.status_code, 200)
        
        # test POST request (fail)
        post_response = self.client.post(self.home_url)
        self.assertEqual(post_response.status_code, 405)
        
        # test PUT request (fail)
        put_response = self.client.put(self.home_url)
        self.assertEqual(put_response.status_code, 405)
        
        # test DELETE request (fail)
        delete_response = self.client.delete(self.home_url)
        self.assertEqual(delete_response.status_code, 405)

# tests for signup view
class SignupViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('signup')
        self.verify_url = reverse('verify_2fa')
        
        self.valid_user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'Password123!',
            'password2': 'Password123!'
        }
        
    # test that signup accepts GET request
    def test_signup_page_loads_correctly(self):
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/signup.html')
        self.assertIsInstance(response.context['form'], SignupForm)
        
    # test invalid data
    def test_signup_form_invalid_data(self):
        # empty data
        response = self.client.post(self.signup_url, {})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/signup.html')
        self.assertTrue(response.context['form'].errors)
        
        # invalid email
        invalid_data = self.valid_user_data.copy()
        invalid_data['email'] = 'not-an-email'
        response = self.client.post(self.signup_url, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/signup.html')
        self.assertIn('email', response.context['form'].errors)
        
        # password mismatch
        invalid_data = self.valid_user_data.copy()
        invalid_data['password2'] = 'DifferentPassword123!'
        response = self.client.post(self.signup_url, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/signup.html')
        self.assertIn('password2', response.context['form'].errors)
    

# testiing login view
class LoginViewTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )
        self.client = Client()
        self.login_url = reverse('login')
        self.verify_url = reverse('verify_2fa')
        
    # test GET request
    def test_login_get_request(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login.html')
        self.assertIsInstance(response.context['form'], LoginForm)
        
    # test valid login
    def test_login_post_valid_form(self):
        with patch('secrets.token_urlsafe', return_value='test_token'):
            response = self.client.post(self.login_url, {
                'email': 'test@example.com',
                'password': 'testpassword123',
            })
            self.assertRedirects(response, self.verify_url)
            self.assertEqual(self.client.session.get('verification_code'), 'test_token')
            self.assertEqual(self.client.session.get('pending_user_id'), self.user.id)
            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].subject, 'Your Login Verification Code')
            self.assertEqual(mail.outbox[0].to, ['test@example.com'])
            self.assertIn('test_token', mail.outbox[0].body)
    
    # test invalid email
    def test_login_post_invalid_form(self):
        response = self.client.post(self.login_url, {
            'email': 'invalid-email',
            'password': 'testpassword123',
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login.html')
        self.assertFalse(response.context['form'].is_valid())
        
    # test email matching with caps
    def test_login_case_insensitive_email(self):
        with patch('secrets.token_urlsafe', return_value='test_token'):
            response = self.client.post(self.login_url, {
                'email': 'TEST@example.com',
                'password': 'testpassword123',
            })
            
            self.assertRedirects(response, self.verify_url)
            self.assertEqual(self.client.session.get('pending_user_id'), self.user.id)

    # test only GET and POST methods are allowed 
    def test_login_http_methods(self):
        response = self.client.put(self.login_url)
        self.assertEqual(response.status_code, 405)
        
        response = self.client.delete(self.login_url)
        self.assertEqual(response.status_code, 405)
    
    # test session variables
    def test_login_session_variables(self):
        with patch('secrets.token_urlsafe', return_value='test_token'):
            response = self.client.post(self.login_url, {
                'email': 'test@example.com',
                'password': 'testpassword123',
            })
            
            self.assertIn('verification_code', self.client.session)
            self.assertIn('pending_user_id', self.client.session)
            self.assertEqual(self.client.session['verification_code'], 'test_token')
            self.assertEqual(self.client.session['pending_user_id'], self.user.id)
    
    # test uniqe tokens are generated for each login
    def test_login_token_generation(self):
        with patch('secrets.token_urlsafe', return_value='token1'):
            response = self.client.post(self.login_url, {
                'email': 'test@example.com',
                'password': 'testpassword123',
            })
            token1 = self.client.session.get('verification_code')
            self.assertIsNotNone(token1, "Verification code not set in session")
        
        self.client.session.flush()
        
        with patch('secrets.token_urlsafe', return_value='token2'):
            response = self.client.post(self.login_url, {
                'email': 'test@example.com',
                'password': 'testpassword123',
            })
            token2 = self.client.session.get('verification_code')
            self.assertIsNotNone(token2, "Verification code not set in session")
        self.assertNotEqual(token1, token2)


# testing password reset confirm view
class PasswordResetConfirmViewTests(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.original_password = "Password123!"
        self.client = Client()
        self.reset_url = reverse('password_reset_confirm', args=[self.user.id])
        self.login_url = reverse('login')
        self.password_reset_url = reverse('password_reset')
    
    # test GET request
    def test_get_request(self):
        response = self.client.get(self.reset_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/password_reset_confirm.html')
        self.assertIsInstance(response.context['form'], PasswordResetConfirmForm)
        
    # test successful password reset
    def test_successful_password_reset(self):
        response = self.client.post(self.reset_url, {
            'password1': 'NewPassword123!',
            'password2': 'NewPassword123!'
        })
        self.assertRedirects(response, self.login_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("successfully", str(messages[0]))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPassword123!'))
        self.assertFalse(self.user.check_password(self.original_password))
        
    # test passwords mismatch
    def test_passwords_dont_match(self):
        response = self.client.post(self.reset_url, {
            'password1': 'NewPassword123!',
            'password2': 'DifferentPassword123!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/password_reset_confirm.html')
        self.assertFalse(response.context['form'].is_valid())
        self.assertTrue(any('password' in field for field in response.context['form'].errors))
        self.assertTrue(any('match' in str(error) for errors in response.context['form'].errors.values() for error in errors))
        
    # test password is too short
    def test_password_too_short(self):
        response = self.client.post(self.reset_url, {
            'password1': 'Short1!',
            'password2': 'Short1!'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/password_reset_confirm.html')
        self.assertFalse(response.context['form'].is_valid())
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.original_password))
        
    # test invaldid id
    def test_invalid_user_id(self):
        invalid_url = reverse('password_reset_confirm', args=[99999])
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)
        
    # test only GET and POST methods are allowed
    def test_http_methods(self):
        response = self.client.put(self.reset_url)
        self.assertEqual(response.status_code, 405)

        response = self.client.delete(self.reset_url)
        self.assertEqual(response.status_code, 405)
        
    # test password complexity requirements
    def test_password_complexity(self):
        response = self.client.post(self.reset_url, {
            'password1': 'ValidPassword123!',
            'password2': 'ValidPassword123!'
        })
        self.assertEqual(response.status_code, 302)
        
    # test empty form
    def test_empty_form_submission(self):
        response = self.client.post(self.reset_url, {})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/password_reset_confirm.html')
        self.assertFalse(response.context['form'].is_valid())
        
    # test password hashing
    def test_password_hashing(self):
        self.client.post(self.reset_url, {
            'password1': 'NewPassword123!',
            'password2': 'NewPassword123!'
        })
        
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.password, 'NewPassword123!')
        self.assertTrue(self.user.check_password('NewPassword123!'))
        
    # test user not found
    def test_user_not_found_exception(self):
        non_existent_user = UserFactory()
        user_id = non_existent_user.id
        non_existent_user.delete()
        reset_url = reverse('password_reset_confirm', args=[user_id])
        response = self.client.get(reset_url)
        self.assertEqual(response.status_code, 404)
        
# testing password reset request view
class PasswordResetRequestTests(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client = Client()
        self.reset_request_url = reverse('password_reset')
        self.login_url = reverse('login')
        
    # test GET request
    def test_get_request(self):
        response = self.client.get(self.reset_request_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/password_reset.html')
        self.assertIsInstance(response.context['form'], PasswordResetForm)
        
    # test valiud reset
    def test_successful_reset_request_existing_user(self):
        response = self.client.post(self.reset_request_url, {
            'email': self.user.email,
        })
        
        # check success
        self.assertRedirects(response, self.login_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("If an account with that email exists", str(messages[0]))
        
        # check email sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Password Reset Request")
        self.assertEqual(mail.outbox[0].to, [self.user.email])
        self.assertIn("reset your password", mail.outbox[0].body)
        self.assertIn(str(self.user.id), mail.outbox[0].body)
        
    # test invalid reset
    def test_reset_request_nonexistent_user(self):
        response = self.client.post(self.reset_request_url, {
            'email': 'nonexistent@example.com',
        })
        
        # check message - no email
        self.assertRedirects(response, self.login_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("If an account with that email exists", str(messages[0]))
        self.assertEqual(len(mail.outbox), 0)
        
    # test uppercase email
    def test_reset_request_case_insensitive_email(self):
        response = self.client.post(self.reset_request_url, {
            'email': self.user.email.upper(),
        })
        
        # test success
        self.assertRedirects(response, self.login_url)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user.email.lower()])

    # test whitespaece in email  
    def test_reset_request_with_whitespace_in_email(self):
        response = self.client.post(self.reset_request_url, {
            'email': f" {self.user.email} ",
        })
        
        # test success
        self.assertRedirects(response, self.login_url)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user.email])
        
    # test invalid email
    def test_reset_request_invalid_email_format(self):
        response = self.client.post(self.reset_request_url, {
            'email': 'not-an-email',
        })
        
        # no redirect - no email
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/password_reset.html')
        self.assertFalse(response.context['form'].is_valid())
        self.assertIn('email', response.context['form'].errors)
        self.assertEqual(len(mail.outbox), 0)
        
    # test no email
    def test_reset_request_empty_email(self):
        response = self.client.post(self.reset_request_url, {
            'email': '',
        })
        
        # no redirect - no email
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/password_reset.html')
        self.assertFalse(response.context['form'].is_valid())
        self.assertIn('email', response.context['form'].errors)
        self.assertEqual(len(mail.outbox), 0)
        
    # test email url
    def test_reset_url_in_email(self):
        response = self.client.post(self.reset_request_url, {
            'email': self.user.email,
        })
        
        email_body = mail.outbox[0].body
        reset_url = [line for line in email_body.split('\n') if 'http' in line][0].strip()
        self.assertIn(reverse('password_reset_confirm', kwargs={'user_id': self.user.id}), reset_url)
        
    # test email failure handling
    def test_email_sending_failure(self):
        with patch('django.core.mail.send_mail', side_effect=Exception('Email sending failed')):
            response = self.client.post(self.reset_request_url, {
                'email': self.user.email,
            })
            
            # redirect - send mail
            self.assertRedirects(response, self.login_url)
            messages = list(get_messages(response.wsgi_request))
            self.assertEqual(len(messages), 1)
            self.assertIn("If an account with that email exists", str(messages[0]))
            
# testing login view
class LogoutViewTests(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client = Client()
        self.logout_url = reverse('logout')
        
    # test GET request
    def test_logout_view_renders_template(self):
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/logout.html')
        
    # test valid logout
    def test_logout_view_logs_out_user(self):
        self.client.force_login(self.user)
        self.assertTrue('_auth_user_id' in self.client.session)
        response = self.client.get(self.logout_url)
        self.assertFalse('_auth_user_id' in self.client.session)

    # test session cleared            
    def test_session_cleared_after_logout(self):
        self.client.force_login(self.user)
        session = self.client.session
        session['test_key'] = 'test_value'
        session.save()   
        response = self.client.get(self.logout_url)
        self.assertNotIn('test_key', self.client.session)
        
    # test POST request    
    def test_post_request_to_logout(self):
        self.client.force_login(self.user)
        response = self.client.post(self.logout_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/logout.html')
        self.assertFalse('_auth_user_id' in self.client.session)
        
    # test logout removes cookies
    def test_logout_removes_auth_cookies(self):
        self.client.force_login(self.user)
        response = self.client.get(self.logout_url)
        self.assertIn('sessionid', response.cookies)
        self.assertEqual(response.cookies['sessionid']['max-age'], 0)

# testing plaid client connection
class PlaidViewsTests(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client = Client()
        self.factory = RequestFactory()
        
        self.create_link_token_url = reverse('create_link_token')
        self.exchange_public_token_url = reverse('exchange_public_token')
        
        self.mock_link_token_response = MagicMock()
        self.mock_link_token_response.link_token = "test_link_token"
        
        self.mock_exchange_response = MagicMock()
        self.mock_exchange_response.access_token = "test_access_token"
        
    # test plaid response
    def test_get_plaid_client(self):
        with patch('plaid.api.plaid_api.PlaidApi') as mock_plaid_api:
            plaid_client = get_plaid_client()
            mock_plaid_api.assert_called_once()
            
    # test creating link token
    def test_create_link_token_authenticated(self):
        self.client.force_login(self.user)
        with patch('app.views.plaid_client.get_plaid_client') as mock_get_client:
            mock_client = MagicMock()
            mock_client.link_token_create.return_value = self.mock_link_token_response
            mock_get_client.return_value = mock_client
            response = self.client.get(self.create_link_token_url)
            
            # check response
            self.assertEqual(response.status_code, 200)
            self.assertEqual(json.loads(response.content)['link_token'], 'test_link_token')
            args, kwargs = mock_client.link_token_create.call_args
            request_data = args[0]
            self.assertEqual(request_data.user['client_user_id'], str(self.user.id))
            
    # test link toekn for unauth user
    def test_create_link_token_unauthenticated(self):
        self.client.logout()
        with patch('app.views.plaid_client.get_plaid_client') as mock_get_client:
            mock_client = MagicMock()
            mock_client.link_token_create.return_value = self.mock_link_token_response
            mock_get_client.return_value = mock_client
            response = self.client.get(self.create_link_token_url)
            
            # check guest user response
            self.assertEqual(response.status_code, 200)
            self.assertEqual(json.loads(response.content)['link_token'], 'test_link_token')
            args, kwargs = mock_client.link_token_create.call_args
            request_data = args[0]
            self.assertEqual(request_data.user['client_user_id'], 'guest_user')
            
    # test POST not allowed
    def test_create_link_token_post_not_allowed(self):
        response = self.client.post(self.create_link_token_url)
        self.assertEqual(response.status_code, 405)
    
    # test token exchange
    def test_exchange_public_token_success(self):
        self.client.force_login(self.user)
        with patch('app.views.plaid_client.get_plaid_client') as mock_get_client:
            mock_client = MagicMock()
            mock_client.item_public_token_exchange.return_value = self.mock_exchange_response
            mock_get_client.return_value = mock_client
            response = self.client.post(
                self.exchange_public_token_url,
                json.dumps({'public_token': 'test_public_token'}),
                content_type='application/json'
            )
            
            # check response
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.content)
            self.assertTrue(response_data['success'])
            self.assertEqual(response_data['message'], 'Access token saved successfully!')
            self.user.refresh_from_db()
            self.assertEqual(self.user.plaid_access_token, 'test_access_token')
            
    # test exchange token requires auth
    def test_exchange_public_token_unauthenticated(self):
        self.client.logout()
        response = self.client.post(
            self.exchange_public_token_url,
            json.dumps({'public_token': 'test_public_token'}),
            content_type='application/json'
        )

        # check redirect
        self.assertEqual(response.status_code, 302)
        login_url = reverse('login')
        self.assertTrue(
            response.url.startswith(login_url) or 
            'login' in response.url or
            'accounts/login' in response.url
        )
        
    # test toek exchange without public token
    def test_exchange_public_token_missing_token(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.exchange_public_token_url,
            json.dumps({}),
            content_type='application/json'
        )

        # check response
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertEqual(response_data['error'], 'Public token is missing.')
        
    # test token exchange without access token  
    def test_exchange_public_token_no_access_token(self):
        self.client.force_login(self.user)
        with patch('app.views.plaid_client.get_plaid_client') as mock_get_client:
            mock_response = MagicMock()
            mock_response.access_token = None
            mock_client = MagicMock()
            mock_client.item_public_token_exchange.return_value = mock_response
            mock_get_client.return_value = mock_client
            
            response = self.client.post(
                self.exchange_public_token_url,
                json.dumps({'public_token': 'test_public_token'}),
                content_type='application/json'
            )
            
            # check response
            self.assertEqual(response.status_code, 400)
            response_data = json.loads(response.content)
            self.assertFalse(response_data['success'])
            self.assertEqual(response_data['error'], 'Access token not received.')
            
    # test GET not allowed
    def test_exchange_public_token_get_not_allowed(self):
        self.client.force_login(self.user)
        response = self.client.get(self.exchange_public_token_url)
        self.assertEqual(response.status_code, 405)

class ProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.profile_url = reverse('profile')

    # test authenticated users can access profile
    def test_profile_view_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/profile.html')

    # test unauthenticated users are redirected to login
    def test_profile_view_unauthenticated(self):
        response = self.client.get(self.profile_url)
        login_url = getattr(settings, 'LOGIN_URL', '/accounts/login/')
        expected_redirect_url = f'{login_url}?next={self.profile_url}'
        self.assertRedirects(
            response, 
            expected_redirect_url, 
            fetch_redirect_response=False
        )

class EditUserViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.edit_url = reverse('edit_user', kwargs={'user_id': self.user.id}) 
        self.client.force_login(self.user)
        
        self.valid_data = {
            'username': 'new_username',
            'email': 'new_email@example.com',
            'current_password': 'Password123!'
        }
        
        self.password_change_data = {
            'username': 'new_username',
            'email': 'new_email@example.com',
            'current_password': 'Password123!',
            'password': 'NewPassword456@',
            'password_confirm': 'NewPassword456@'
        }

    # test successful user edit
    def test_edit_user_success(self):
        response = self.client.post(
            self.edit_url,
            data=json.dumps(self.valid_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'success': True})
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'new_username')
        self.assertEqual(self.user.email, 'new_email@example.com')

    # test successful user edit with password change
    def test_edit_user_with_password_change(self):
        response = self.client.post(
            self.edit_url,
            data=json.dumps(self.password_change_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'success': True})
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'new_username')
        self.assertEqual(self.user.email, 'new_email@example.com')
        self.assertTrue(self.user.check_password('NewPassword456@'))

    # test unath user edit
    def test_edit_user_unauthorized(self):
        other_user = UserFactory()
        other_user_url = reverse('edit_user', kwargs={'user_id': other_user.id})
        
        response = self.client.post(
            other_user_url,
            data=json.dumps(self.valid_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.content), {'error': 'Unauthorized'})

    # test edit wrong password
    def test_edit_user_wrong_password(self):
        invalid_data = self.valid_data.copy()
        invalid_data['current_password'] = 'WrongPassword123!'
        
        response = self.client.post(
            self.edit_url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content), {'error': 'Incorrect current password.'})

    # test edit without required fields
    def test_edit_user_missing_fields(self):
        invalid_data = {
            'username': 'new_username',
        }
        
        response = self.client.post(
            self.edit_url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content), {'error': 'Username, email, and current password are required.'})

    # test edit fails with duplicate username
    def test_edit_user_duplicate_username(self):
        other_user = UserFactory(username='existing_username')
        
        invalid_data = self.valid_data.copy()
        invalid_data['username'] = 'existing_username'
        
        response = self.client.post(
            self.edit_url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content), {'error': 'Username already exists.'})

    # test edit fails with duplicate email
    def test_edit_user_duplicate_email(self):
        other_user = UserFactory(email='existing@example.com')
        
        invalid_data = self.valid_data.copy()
        invalid_data['email'] = 'existing@example.com'
        
        response = self.client.post(
            self.edit_url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content), {'error': 'Email already exists.'})

    # test edit fail with password mismatch
    def test_edit_user_password_mismatch(self):
        invalid_data = self.valid_data.copy()
        invalid_data['password'] = 'NewPassword456@'
        invalid_data['password_confirm'] = 'DifferentPassword789#'
        
        response = self.client.post(
            self.edit_url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content), {'error': 'Passwords do not match.'})

    # test edit fails when password short
    def test_edit_user_password_too_short(self):
        invalid_data = self.valid_data.copy()
        invalid_data['password'] = 'Short1!'
        invalid_data['password_confirm'] = 'Short1!'
    
        response = self.client.post(
            self.edit_url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content), {'error': 'Password must be at least 8 characters long.'})

    # test edit fail when password has no uppercases
    def test_edit_user_password_no_uppercase(self):
        invalid_data = self.valid_data.copy()
        invalid_data['password'] = 'password123!'
        invalid_data['password_confirm'] = 'password123!'
        
        response = self.client.post(
            self.edit_url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content), {'error': 'Password must contain at least one uppercase letter.'})

    # test edit fails when password has no numbers
    def test_edit_user_password_no_number(self):
        invalid_data = self.valid_data.copy()
        invalid_data['password'] = 'Password!'
        invalid_data['password_confirm'] = 'Password!'
        
        response = self.client.post(
            self.edit_url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content), {'error': 'Password must contain at least one number.'})

    # test edit fails when password has no special chars
    def test_edit_user_password_no_special_char(self):
        invalid_data = self.valid_data.copy()
        invalid_data['password'] = 'Password123'
        invalid_data['password_confirm'] = 'Password123'
        
        response = self.client.post(
            self.edit_url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content), {'error': 'Password must contain at least one special character (!@#$%^&*.).'})

    # test edit fails when password is username
    def test_edit_user_password_same_as_username(self):
        invalid_data = self.valid_data.copy()
        invalid_data['username'] = 'TestUser123!'
        invalid_data['password'] = 'TestUser123!'
        invalid_data['password_confirm'] = 'TestUser123!'
        
        response = self.client.post(
            self.edit_url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content), {'error': 'Password cannot be the same as your username.'})

    # test edit fails when new password email
    def test_edit_user_password_same_as_email(self):
        invalid_data = self.valid_data.copy()
        invalid_data['email'] = 'Password123!@example.com'
        invalid_data['password'] = 'Password123!@example.com'
        invalid_data['password_confirm'] = 'Password123!@example.com'
        
        response = self.client.post(
            self.edit_url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content), {'error': 'Password cannot be the same as your email.'})

    # test database error handling
    @patch('app.views.CustomUser.objects')
    def test_edit_user_server_error(self, mock_objects):
        mock_objects.exclude.side_effect = Exception("Database error")
        mock_objects.all.side_effect = Exception("Database error")
        
        response = self.client.post(
            self.edit_url,
            data=json.dumps(self.valid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 500)
        self.assertEqual(json.loads(response.content), {'error': 'Database error'})


class DeleteAccountViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.delete_url = reverse('delete_account')
        self.client.force_login(self.user)

    # test valid account deletion
    def test_delete_account_success(self):
        user_id = self.user.id
        
        response = self.client.post(self.delete_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'success': True})
        
        with self.assertRaises(CustomUser.DoesNotExist):
            CustomUser.objects.get(id=user_id)

    # test unauthenticated users cannot delete accounts
    def test_delete_account_unauthenticated(self):
        self.client.logout()
        
        response = self.client.post(self.delete_url)
        
        login_url = getattr(settings, 'LOGIN_URL', '/accounts/login/')
        expected_redirect_url = f'{login_url}?next={self.delete_url}'
        self.assertRedirects(
            response, 
            expected_redirect_url, 
            fetch_redirect_response=False
        )

    # test database error handling
    @patch('app.views.CustomUser.delete')
    def test_delete_account_server_error(self, mock_delete):
        mock_delete.side_effect = Exception("Database error")
        
        response = self.client.post(self.delete_url)
        
        self.assertEqual(response.status_code, 500)
        self.assertEqual(json.loads(response.content), {'error': 'Database error'})