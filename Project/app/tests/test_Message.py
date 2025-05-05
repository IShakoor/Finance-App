from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
from app.models import Message
from app.tests.factories import MessageFactory, UserFactory

class MessageModelTests(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.message = MessageFactory(user=self.user)
    
    # test valid creation
    def test_message_creation(self):
        self.assertIsInstance(self.message, Message)
        self.assertEqual(str(self.message), self.message.title)
    
    # test saving fields correctly
    def test_message_fields(self):
        self.assertEqual(self.message.user, self.user)
        self.assertIsNotNone(self.message.title)
        self.assertIsNotNone(self.message.content)
        self.assertIsInstance(self.message.is_read, bool)
        self.assertIsNotNone(self.message.created_at)
    
    # test that messages are linked to user correctly
    def test_message_user_relationship(self):
        self.assertIn(self.message, self.user.messages.all())
        
        message2 = MessageFactory(user=self.user)
        self.assertEqual(self.user.messages.count(), 2)
    
    # test deleting user deletes message
    def test_message_deletion_on_user_delete(self):
        message_id = self.message.id
        self.user.delete()
        with self.assertRaises(Message.DoesNotExist):
            Message.objects.get(id=message_id)
    
    # test message is_read defaults to false
    def test_message_default_is_read(self):
        new_message = Message.objects.create(
            user=self.user,
            title="Test Title",
            content="Test Content"
        )
        self.assertFalse(new_message.is_read)
    
    # test created_at is automatically set 
    def test_message_created_at_auto_now(self):
        now = timezone.now()
        new_message = Message.objects.create(
            user=self.user,
            title="Test Title",
            content="Test Content"
        )
        self.assertLessEqual(new_message.created_at, now + timedelta(seconds=1))
        self.assertGreaterEqual(new_message.created_at, now - timedelta(seconds=1))
    
    # test title cannot exceed max length
    def test_message_title_max_length(self):
        with self.assertRaises(ValidationError):
            message = Message(
                user=self.user,
                title="A" * 256,
                content="Test Content"
            )
            message.full_clean()
    
    # test encryption works
    def test_encrypted_content_field(self):
        test_content = "This is sensitive information"
        message = Message.objects.create(
            user=self.user,
            title="Secret Message",
            content=test_content
        )
        
        # get value from database
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute(
            "SELECT content FROM app_message WHERE id = %s", 
            [message.id]
        )
        raw_content = cursor.fetchone()[0]
        
        # The raw content should not be same as original due to encryption
        self.assertNotEqual(raw_content, test_content)
        
        # if data retrieved through model it should decrypt
        retrieved_message = Message.objects.get(id=message.id)
        self.assertEqual(retrieved_message.content, test_content)
    
    # test bulk message creation
    def test_bulk_message_creation(self):
        messages = MessageFactory.create_batch(5, user=self.user)
        self.assertEqual(len(messages), 5)
        for message in messages:
            self.assertEqual(message.user, self.user)