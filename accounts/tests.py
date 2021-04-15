from django.test import TestCase
from django.contrib.auth import get_user, get_user_model
# Create your tests here.

User = get_user_model()

class UserTestCase(TestCase): 
    def setUp(self):
        usr1 = User(username = 'abc', email = 'abc@gm.com')
        usr1.password = 'abc'
        usr1.is_staff = True
        usr1.is_superuser = True
        usr1.save()
        print(User.id)
    
    def test_user_exisits(self):
        usrexist = User.objects.all().count()
        print(usrexist)
        self.assertEqual(usrexist, 1)
        self.assertNotEqual(usrexist, 0)

    def test_user_password(self):
        user_qs = User.objects.filter(username = 'abc').first()
        print(user_qs.password)
        self.assertEqual(user_qs.password , 'abc')
        self.assertNotEqual(user_qs.password, '')

    def test_login_url(self):
        login_url = '/auth/'
        # self.assertEqual('/auth/', login_url)
        # response = self.client.post(login_url, {}, follow=True)
        data = {'username':'admin', 'password' : 'admin'}
        response = self.client.post(login_url, data, 
        follow=True)
        print(dir(response))
        status_code = response.status_code
        redirect_path = response.request.get('PATH_INFO')
        self.assertEqual(redirect_path, '/shop/')
        self.assertEqual(status_code, 200)