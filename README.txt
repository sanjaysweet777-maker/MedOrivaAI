MedOriva AI — demonstration workspace

This branch fixes unsafe translation reconstruction and updates the demo website.
It is not clinically validated and must use fictional demonstration information.

RUN
  python -m pip install -r requirements.txt
  gunicorn app:app --bind 0.0.0.0:10000

HOST ENVIRONMENT (set on Render; do not put secrets in GitHub or chat)
  SECRET_KEY: a long randomly generated secret, shared by all workers
  COOKIE_SECURE: true for the HTTPS hosted application
  DEMO_EMAIL: your reviewer login email
  DEMO_PASSWORD: a strong reviewer password
  GOOGLE_TRANSLATE_API_KEY: a key for an enabled Google Cloud Translation API

Default credentials remain available for a public fictional-data demo. Overriding
DEMO_EMAIL or DEMO_PASSWORD removes the public credential box. Set SECRET_KEY in
hosted deployments: the development fallback is random per process, so it does not
support stable multi-worker sessions. There is no production account-management,
rate-limiting or clinical deployment assurance in this prototype.

TRANSLATION BEHAVIOUR
- 12 exact staff phrases x 9 languages are prepared demo entries. Eight concern
  basic symptom communication and four concern reception/appointments. These
  entries need independent bilingual review; code tests do not validate wording.
- Four exact romanised Tamil utterances cover two chest-pain meanings, positive
  and negative. Extra clauses, durations and third-person wording are not inferred.
- Native-script input is preserved alongside the English translation. Polish,
  Somali and Romanian correctly use their normal Latin-script input.
- Other full messages use the official Google Cloud Translation Basic v2 API.
  The selected language is sent explicitly; plain-text format and bounded timeouts
  are used. No unofficial Google scraping or MyMemory fallback is used.
- Without an API key only prepared phrases are available. Other results explicitly
  say unavailable; the original text is never labelled a successful translation.
- Unchanged/empty output, unexpected writing systems, changed numeric tokens,
  malformed replies and service failures are withheld. These checks do not detect
  all meaning errors: negation, pronouns, units, names, dialect and contextual meaning
  still require review. Number words and native digits may produce conservative
  false rejections. Script checks do not establish the language of Latin-script text.
- No symptom-based sentence reconstruction, clinical urgency decision or automatic
  confirmation of understanding. Staff review remains necessary.
- Plain-language suggestions are optional and require staff acceptance before the
  edited text is translated. Original messages are otherwise translated unchanged.
- Conversation content is not placed in the Flask session, app database or a shared
  translation cache. The browser displays it until the session ends. Full-text
  requests go to Google Cloud; provider and host retention/processing settings
  must be reviewed before any real personal information is used. Closing a browser
  is not a guarantee of erasure from provider or hosting infrastructure.
- Context selects guided prompts; free text remains available. This is not a
  semantic topic-enforcement or clinical safety boundary.
- Online contact submission is not connected and cannot falsely report delivery.

CHECKS
  python -m unittest discover -s tests -v
  node --check static/js/app.js

Tests use mocked provider responses and cover all language paths, exact matching,
complete-message forwarding, Unicode marks, numbers, failures, session lifecycle,
input validation, rendered routes and optional simplification. Independent bilingual
review, live authenticated provider testing and browser visual/interaction testing
remain outstanding. No claim of 100% translation accuracy is made.

DEMONSTRATION
1. Sign in and choose Reception plus a language. Try 'Do you have an appointment?'.
2. Choose Appointment and try 'Do you need an interpreter?'.
3. Choose Basic Symptoms and try 'Do you have chest pain?'.
4. For Tamil, try 'enaku nenji vali irukku' and 'enaku nenji vali illa'.
5. Try a longer romanised Tamil sentence. It must ask for native-script input,
   rather than dropping words to fit a stock sentence.
6. With the service configured, test complete fictional native-language sentences
   including negation, multiple symptoms, third-person subjects, timing and numbers.
   Have independent bilingual reviewers assess each source/target pair.
7. End the session; the displayed conversation clears and another session can start.

ROADMAP AND CLAIMS
Nine languages is MVP interface/provider scope, not nine clinically validated
languages. 130+ provider-supported languages remains a commercial-launch target,
subject to API availability/configuration and separate healthcare validation.
NHS approval, DCB0129 conformity and DTAC assessment are not claimed.

Provider reference:
https://docs.cloud.google.com/translate/docs/reference/rest/v2/translate
