import os
import unittest
from unittest.mock import patch, Mock
import requests
import translation_engine as engine
from app import app

class TranslationTests(unittest.TestCase):
    def test_prepared_phrases_all_languages(self):
        for language in engine.LANGUAGES:
            for original, translations in engine.STAFF_LOOKUP.items():
                with self.subTest(language=language,original=original):
                    result=engine.staff_translation(original,language)
                    self.assertEqual(result.source,'prepared_phrase')
                    self.assertEqual(result.text,translations[language])
                    self.assertTrue(engine.script_matches(result.text,language))
                    self.assertEqual(result.status,'needs_review')
    def test_combining_marks_preserved(self):
        text='எனக்கு நெஞ்சு வலி இல்லை'
        self.assertEqual(engine.normalise(text),text)
    def test_full_sentences_never_reconstructed(self):
        cases=[('pl','Nie mam gorączki, ale mam ból w klatce piersiowej.'),('ro','Mama mea are durere în piept de 3 zile.'),('so','Ma qabo madax xanuun, laakiin waxaan qabaa qandho.'),('ta','எனக்கு காய்ச்சல் இல்லை ஆனால் நெஞ்சு வலி இருக்கிறது.')]
        for code,text in cases:
            with self.subTest(code=code),patch.object(engine,'online',return_value=engine.Translation('Complete message',status='needs_review')) as online:
                engine.patient_translation(text,code)
                online.assert_called_once_with(text,code,'en')
    def test_compound_staff_question_no_partial_lookup(self):
        text='Do you have chest pain or does your mother have a fever?'
        with patch.object(engine,'online',return_value=engine.Translation()) as online:
            engine.staff_translation(text,'ta');online.assert_called_once_with(text,'en','ta')
    def test_exact_thanglish_only(self):
        self.assertEqual(engine.patient_translation('enaku nenji vali irukku','ta').text,'I have chest pain.')
        self.assertEqual(engine.patient_translation('enaku nenji vali illa','ta').text,'I do not have chest pain.')
        for text in ('enaku nenji vali irukku 3 naala','my mother enaku nenji vali irukku','enaku nenji vali illa but fever'):
            with self.subTest(text=text):self.assertEqual(engine.patient_translation(text,'ta').status,'unavailable')
    def test_latin_languages_use_selected_source(self):
        for code,text in [('pl','Mam ból głowy.'),('so','Waxaan qabaa madax xanuun.'),('ro','Am o durere de cap.')]:
            with patch.object(engine,'online',return_value=engine.Translation()) as online:
                engine.patient_translation(text,code);online.assert_called_once_with(text,code,'en')
    def test_provider_missing_no_fake_success(self):
        with patch.dict(os.environ,{},clear=True):
            self.assertEqual(engine.online('hello','en','ta').text,'')
    def test_native_script_not_back_translated(self):
        with patch.object(engine,'online',return_value=engine.Translation('I have no fever.')) as online:
            r=engine.patient_translation('எனக்கு காய்ச்சல் இல்லை.','ta')
            self.assertEqual(r.native,'எனக்கு காய்ச்சல் இல்லை.');self.assertEqual(online.call_count,1)
    def provider(self,text):
        response=Mock();response.json.return_value={'data':{'translations':[{'translatedText':text}]}}
        return response
    @patch.dict(os.environ,{'GOOGLE_TRANSLATE_API_KEY':'test-not-real'})
    def test_provider_contract_and_escaping(self):
        with patch.object(engine.requests,'post',return_value=self.provider('Do not take 5 mg.')) as post:
            r=engine.online('5 mg எடுத்துக்கொள்ள வேண்டாம்.','ta','en')
            self.assertEqual(r.text,'Do not take 5 mg.');self.assertEqual(r.status,'needs_review')
            self.assertEqual(post.call_args.kwargs['json']['source'],'ta');self.assertEqual(post.call_args.kwargs['json']['format'],'text')
            self.assertEqual(post.call_args.kwargs['timeout'],(3,12))
    @patch.dict(os.environ,{'GOOGLE_TRANSLATE_API_KEY':'test-not-real'})
    def test_numeric_change_withheld(self):
        for output in ['Take 25 mg.','Take 2,5 mg.']:
            with patch.object(engine.requests,'post',return_value=self.provider(output)):
                self.assertEqual(engine.online('2.5 mg எடுத்துக்கொள்ளுங்கள்.','ta','en').status,'unavailable')
    @patch.dict(os.environ,{'GOOGLE_TRANSLATE_API_KEY':'test-not-real'})
    def test_wrong_script_echo_blank_and_malformed_withheld(self):
        for output in ['Hello','', 'Bonjour']:
            with patch.object(engine.requests,'post',return_value=self.provider(output)):
                self.assertEqual(engine.online('Hello','en','ta').status,'unavailable')
        with patch.object(engine.requests,'post',return_value=Mock(json=lambda:{})):
            self.assertEqual(engine.online('Hello','en','ta').status,'unavailable')
    @patch.dict(os.environ,{'GOOGLE_TRANSLATE_API_KEY':'test-not-real'})
    def test_timeout_no_fallback(self):
        with patch.object(engine.requests,'post',side_effect=requests.Timeout) as post:
            self.assertEqual(engine.online('Hello','en','ta').status,'unavailable');self.assertEqual(post.call_count,1)

class Routes(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True,SECRET_KEY='test-key')
        self.client=app.test_client()
        self.client.post('/login',json={'email':'demo@medoriva.com','password':'medoriva2026'})
    def start(self,code='ta',context='Basic Symptoms'):
        return self.client.post('/api/start_session',json={'context':context,'lang_code':code})
    def test_all_contexts_have_prepared_prompts(self):
        for context in ('Reception','Appointment','Basic Symptoms'):
            for code in engine.LANGUAGES:
                d=self.start(code,context).get_json();self.assertTrue(d['prepared_prompts'])
    def test_requires_active_session(self):
        self.assertEqual(self.client.post('/api/translate_staff',json={'text':'Hello'}).status_code,409)
    def test_invalid_parameters(self):
        for code,context in [('xx','Reception'),('ta','fake'),([], 'Reception')]:self.assertEqual(self.start(code,context).status_code,400)
        self.start()
        for text in [None,[],12,'','x'*2001]:self.assertEqual(self.client.post('/api/translate_staff',json={'text':text}).status_code,400)
        self.assertEqual(self.client.post('/api/translate_staff',json=[]).status_code,400)
    def test_translation_original_and_no_clinical_inference(self):
        self.start()
        d=self.client.post('/api/translate_patient',json={'text':'enaku nenji vali illa'}).get_json()
        self.assertEqual(d['original'],'enaku nenji vali illa');self.assertFalse(d['medical_alert']);self.assertIsNone(d['is_negative'])
        self.assertEqual(d['status'],'needs_review')
    def test_simplification_is_optional(self):
        self.start()
        original='Please commence prior to approximately 5 pm.'
        d=self.client.post('/api/simplify',json={'text':original}).get_json();self.assertTrue(d['changed'])
        with patch('app.staff_translation',return_value=engine.Translation()) as translate:
            self.client.post('/api/translate_staff',json={'text':original});translate.assert_called_once_with(original,'ta')
    def test_end_session_clears_context_preserves_login(self):
        self.start();self.client.post('/api/end_session',json={})
        self.assertFalse(self.client.get('/api/session_status').get_json()['active'])
        self.assertEqual(self.start().status_code,200)
    def test_pages_and_static_assets(self):
        for path in ['/','/portal','/static/css/public.css','/static/css/style.css','/static/js/app.js']:
            with self.client.get(path) as response: self.assertEqual(response.status_code,200)
        anonymous=app.test_client();self.assertEqual(anonymous.get('/login').status_code,200)
        self.assertEqual(anonymous.post('/api/translate_staff',json={'text':'hello'}).status_code,401)
    def test_transcripts_not_in_session(self):
        self.start();self.client.post('/api/translate_patient',json={'text':'enaku nenji vali irukku'})
        with self.client.session_transaction() as session:
            self.assertNotIn('nenji',str(dict(session)))
    def test_contact_does_not_claim_delivery(self):
        self.assertEqual(self.client.post('/api/contact',json={'name':'Test'}).status_code,503)
    def test_cross_origin_rejected(self):
        self.assertEqual(self.client.post('/api/start_session',json={},headers={'Origin':'https://other.invalid'}).status_code,403)

if __name__=='__main__':unittest.main()
