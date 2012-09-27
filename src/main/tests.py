"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from json import loads

from django.test import TestCase


#class SimpleTest(TestCase):
#    def test_basic_addition(self):
#        """
#        Tests that 1 + 1 always equals 2.
#        """
#        self.assertEqual(1 + 1, 2)


class RegisterTest(TestCase):
    def setUp(self):
        self.client.post(
            '/register/',
            {
                'username': 'abc',
                'email': 'abc@abc.com',
                'password': '1234',
                'password2': '1234'
            }
        )
    
    def test_username(self):
        response = self.client.post(
            '/register/',
            {
                'username': '',
                'email': 'abcabc.com',
                'password': '1234',
                'password2': '12345'
            }
        )
        self.assertEquals(response.context['error_msg'], 'need username')
        
        response = self.client.post(
            '/register/',
            {
                'username': 'abc',
                'email': 'abc@abc.com',
                'password': '1234',
                'password2': '1234'
            }
        )
        self.assertEquals(response.context['error_msg'],
                          'username already exists')

    def test_email(self):
        response = self.client.post(
            '/register/',
            {
                'username': 'abcd',
                'email': '',
                'password': '1234',
                'password2': '12345'
            }
        )
        self.assertEquals(response.context['error_msg'],
                          'need email or email not valid')
        
        response = self.client.post(
            '/register/',
            {
                'username': 'abcd',
                'email': 'abc.com',
                'password': '1234',
                'password2': '12345'
            }
        )
        self.assertEquals(response.context['error_msg'],
                          'need email or email not valid')
        
        response = self.client.post(
            '/register/',
            {
                'username': 'abcd',
                'email': 'abc@abc.com',
                'password': '1234',
                'password2': '1234'
            }
        )
        self.assertEquals(response.context['error_msg'], 'email already exists')
        
    def test_password(self):
        response = self.client.post(
            '/register/',
            {
                'username': 'abcd',
                'email': 'abcd@abcd.com',
                'password': '12',
                'password2': '12345'
            }
        )
        
        self.assertEquals(response.context['error_msg'],
                          'need password, at least 4 character')
        
        response = self.client.post(
            '/register/',
            {
                'username': 'abcd',
                'email': 'abcd@abcd.com',
                'password': '12346',
                'password2': '12345'
            }
        )
        
        self.assertEquals(response.context['error_msg'],
                          'two password not same')
        
        
class LoginTest(TestCase):
    def setUp(self):
        self.client.post(
            '/register/',
            {
                'username': 'abc',
                'email': 'abc@abc.com',
                'password': '1234',
                'password2': '1234'
            }
        )
    
    def test_username(self):
        response = self.client.post(
            '/login/',
            {
                'username': '  ',
                'password': '1234'
            }
        )
        self.assertEquals(loads(response.content), 'need username and password')
        
        response = self.client.post(
            '/login/',
            {
                'username': '1234',
                'password': '1234'
            }
        )
        self.assertEquals(loads(response.content), 'username does not exist')
        
    def test_password(self):
        response = self.client.post(
            '/login/',
            {
                'username': 'abc',
                'password': ' '
            }
        )
        self.assertEquals(loads(response.content), 'need username and password')
        
        response = self.client.post(
            '/login/',
            {
                'username': 'abc',
                'password': 'abcd'
            }
        )
        self.assertEquals(loads(response.content), 'wrong password')

    def test_success(self):
        response = self.client.post(
            '/login/',
            {
                'username': 'abc',
                'password': '1234'
            }
        )
        self.assertEquals(loads(response.content), 'login success')
