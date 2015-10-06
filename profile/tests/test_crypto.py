from datetime import date

from django.test import TestCase

from ..crypto import *

class CryptoTestCase(TestCase):

    def test_token(self):
        
        user_username = 'user_username'
        user_email = 'user_email'
        due_date = date.today()
        
        original_msg = user_username + ',' + user_email + ',' + due_date.strftime("%Y-%m-%d")
        
        access_token = user_activation_token(user_username, user_email, due_date)
        
        decrypted_msg = decrypt(access_token)
        
        self.assertEqual(original_msg, decrypted_msg)

    def test_encrypt_decrypt(self):
        
        msg = 'message to encrypt super secret'
        
        crypted_msg = encrypt(msg)
        
        self.assertNotEqual(msg, crypted_msg)
        
        decrypted_msg = decrypt(crypted_msg)

        self.assertEqual(msg, decrypted_msg)