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

Hosted access is disabled unless both DEMO_EMAIL and DEMO_PASSWORD are configured.
Public sample credentials are available only for local fictional-data development
when ALLOW_PUBLIC_DEMO=true is explicitly set. Set SECRET_KEY in hosted deployments:
the development fallback is random per process, so it does not support stable
multi-worker sessions. The private demonstration includes a basic per-process login
attempt limit; production still requires per-organisation accounts, centralised
rate limiting, role-based access and formal deployment assurance.

TRANSLATION BEHAVIOUR
- 9 exact staff phrases x 9 languages are prepared demo entries, comprising five
  reception/administrative and four symptom-related prompts. These entries need
  independent bilingual review; code tests do not validate wording.
- Two exact romanised Tamil utterances in the engine cover positive and negative
  chest-pain statements ('enaku nenji vali irukku' and 'enaku nenji vali illa');
  the broader 666-entry dictionary covers tested phrases across languages separately.
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
- Google states that Cloud Translation request text is held briefly in memory and is
  not used to train its translation models. The Basic v2 endpoint used here is global;
  it cannot be configured to keep processing within a specific region. This still
  requires a DPIA, supplier/data-processing terms and transfer assessment before live use.
- Context selects guided prompts; free text remains available. This is not a
  semantic topic-enforcement or clinical safety boundary.
- The website does not collect contact-form data. Its direct email link opens the
  visitor's email service and warns against sending patient-identifiable information.

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
3. Choose Reason for Contact and try a routine care-navigation request.
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
NHS approval, DCB0129 conformity and completed DTAC assessment are not claimed.
Before organisation-approved live use, MedOriva must complete an applicability review,
the required clinical-risk documentation and Clinical Safety Officer review, a DPIA and
data-flow assessment, supplier/transfer due diligence, security testing, accessibility
evidence and the organisation's approval process.

Provider reference:
https://docs.cloud.google.com/translate/docs/reference/rest/v2/translate

DEPLOYMENT FOLLOW-UP
The setup screen now includes Translation connection > Check connection. This
makes one real provider call with a fixed appointment question, bypassing the
prepared phrase bank. A configured key is not treated as proof of a working
connection. The result distinguishes missing configuration, invalid credentials,
API disabled, billing, key restrictions/permissions, quota, timeouts and response
validation failures. Raw provider messages, keys and project IDs are not exposed.
The endpoint requires a signed-in user. Do not paste API keys into chat or GitHub.
GOOGLE_CLOUD_TRANSLATION_API_KEY and GOOGLE_API_KEY are also accepted as deployment
aliases; GOOGLE_TRANSLATE_API_KEY takes precedence. Surrounding whitespace is
removed. The provider's permissions, service enablement, billing and account-level
settings still need to be configured in Google Cloud.
Numbers and numeric times/dates entered as patient answers are preserved verbatim
without unnecessary translation or script rejection. Their interpretation still
needs confirmation; no date conversion or numeric meaning is inferred.
The compact layout uses the available viewport height with independently scrolling
conversation content. Contact email/phone are restored from the original public
site. Copyright year is generated on the server. Public wording focuses on shared
understanding, while development/validation details remain available on expansion.
