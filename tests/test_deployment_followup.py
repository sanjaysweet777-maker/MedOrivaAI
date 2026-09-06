import os
import unittest
from unittest.mock import Mock, patch
import requests
import translation_engine as engine
from app import app

class DeploymentTranslationTests(unittest.TestCase):
    def test_common_key_names_and_whitespace(self):
        for name in ('GOOGLE_TRANSLATE_API_KEY','GOOGLE_CLOUD_TRANSLATION_API_KEY','GOOGLE_API_KEY'):
            with self.subTest(name=name), patch.dict(os.environ,{name:'  example-key  '},clear=True):
                self.assertEqual(engine.configured_key(),'example-key')
        with patch.dict(os.environ,{'GOOGLE_TRANSLATE_API_KEY':'   '},clear=True):
            self.assertEqual(engine.configured_key(),'')
    def test_distinct_google_errors_without_sensitive_details(self):
        for status, reason, expected in [(400,'API_KEY_INVALID','invalid_key'),(403,'SERVICE_DISABLED','api_disabled'),(403,'BILLING_DISABLED','billing'),(403,'API_KEY_HTTP_REFERRER_BLOCKED','access_denied'),(429,'','quota'),(503,'','provider_error')]:
            response=Mock(status_code=status)
            response.json.return_value={'error':{'message':'private project / secret-key / patient text','details':[{'reason':reason}]}}
            with self.subTest(reason=reason):
                result=engine.provider_error(response)
                self.assertEqual(result.error_code,expected)
                self.assertEqual(result.text,'')
                self.assertNotIn('private',result.warning)
                self.assertNotIn('secret',result.warning)
    @patch.dict(os.environ,{'GOOGLE_TRANSLATE_API_KEY':'test-key'},clear=True)
    def test_http_error_reaches_diagnostics(self):
        response=Mock(status_code=403)
        response.json.return_value={'error':{'details':[{'reason':'SERVICE_DISABLED'}]}}
        response.raise_for_status.side_effect=requests.HTTPError(response=response)
        with patch.object(engine.requests,'post',return_value=response):
            self.assertEqual(engine.online('Hello','en','ta').error_code,'api_disabled')
    @patch.dict(os.environ,{'GOOGLE_TRANSLATE_API_KEY':'test-key'},clear=True)
    def test_timeout_and_connection_are_distinct(self):
        for exception,expected in [(requests.Timeout,'timeout'),(requests.ConnectionError,'connection')]:
            with patch.object(engine.requests,'post',side_effect=exception):
                self.assertEqual(engine.online('Hello','en','ta').error_code,expected)
    def test_numeric_answers_preserve_exact_value_without_provider(self):
        for language in engine.LANGUAGES:
            for text in ('3','10:30','12/09','2.5','٢'):
                with self.subTest(language=language,text=text),patch.object(engine,'online') as online:
                    result=engine.patient_translation(text,language)
                    self.assertEqual(result.text,text)
                    self.assertEqual(result.source,'original_value')
                    online.assert_not_called()
        self.assertFalse(engine.numeric_response('2 mg'))
        self.assertFalse(engine.numeric_response('3 days no pain'))
    def test_patient_error_code_is_preserved(self):
        with patch.object(engine,'online',return_value=engine.unavailable('billing')):
            self.assertEqual(engine.patient_translation('எனக்கு காய்ச்சல் இல்லை.','ta').error_code,'billing')

class DeploymentRoutes(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True,SECRET_KEY='test-key')
        self.client=app.test_client()
        self.client.post('/login',json={'email':'demo@medoriva.com','password':'medoriva2026'})
    def test_connection_check_auth_and_fixed_sample(self):
        self.assertEqual(app.test_client().post('/api/translation_check',json={}).status_code,401)
        with patch('app.online',return_value=engine.Translation('உங்களுக்கு முன்பதிவு செய்யப்பட்ட சந்திப்பு உள்ளதா?',source='google_cloud',status='needs_review')) as online:
            result=self.client.post('/api/translation_check',json={'lang_code':'ta','text':'Do not forward private input'}).get_json()
            online.assert_called_once_with('Do you have an appointment?','en','ta')
            self.assertTrue(result['connected'])
        self.assertEqual(self.client.post('/api/translation_check',json={'lang_code':[]}).status_code,400)
    def test_configuration_is_not_mistaken_for_connection(self):
        with patch('app.configured_key',return_value='test-key'),patch('app.online',return_value=engine.unavailable('billing')):
            d=self.client.post('/api/translation_check',json={}).get_json()
            self.assertTrue(d['configured']);self.assertFalse(d['connected'])
            self.assertEqual(d['error_code'],'billing');self.assertNotIn('test-key',str(d))
    def test_contact_copyright_and_constructive_copy_render(self):
        page=self.client.get('/').get_data(as_text=True)
        self.assertIn('mailto:sanjaythillai@gmail.com',page)
        self.assertIn('tel:+447778095553',page)
        self.assertIn('MedOriva AI Ltd. All rights reserved.',page)
        self.assertIn('Built for shared understanding',page)
        self.assertNotIn('Translations can be wrong.',page)
        self.assertNotIn('Human review matters',page)
        portal=self.client.get('/portal').get_data(as_text=True)
        self.assertIn('id="connectionResult"',portal)
        self.assertNotIn('Not a medical device',portal)

if __name__=='__main__':unittest.main()
