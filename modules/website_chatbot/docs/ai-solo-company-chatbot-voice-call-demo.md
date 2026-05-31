# AI Solo Company Chatbot Voice-Call Demo

This demo shows the intended website experience: the visitor uses the normal Easiio chatbot interface and clicks **Start voice call** from inside the chatbot panel.

## Local file

```text
/home/jianl/.hermes/tools/website_chatbot/widget/ai-solo-company-voice-chatbot.html
```

## Public Hermes Proxy URLs

Website/demo page:

```text
https://hermesproxy.easiiodev.ai/p/VaYZmN7v5naw-ai-solo-chatbot-demo/ai-solo-company-voice-chatbot.html
```

Text chatbot API:

```text
https://hermesproxy.easiiodev.ai/p/VaYZmN7v5naw-chatbot-api/
```

Voice-call API:

```text
https://hermesproxy.easiiodev.ai/p/VaYZmN7v5naw-voice-api/
```

## Required widget attributes

```html
data-site-id="ai-solo-company"
data-api-base="https://hermesproxy.easiiodev.ai/p/VaYZmN7v5naw-chatbot-api"
data-voice-call-enabled="true"
data-voice-call-api-base="https://hermesproxy.easiiodev.ai/p/VaYZmN7v5naw-voice-api"
data-voice-call-label="Start voice call"
```

## Visitor flow

1. Open the AI Solo Company page.
2. Click the chatbot bubble.
3. Click **Start voice call**.
4. Click **Record turn** and grant microphone permission.
5. Speak one short question.
6. Click **Stop recording**.
7. The voice backend transcribes, answers, and returns the response to the chatbot thread.
8. Click **End call** when finished.

## Safety boundary

This page is website-facing and review-first:

- no admin token is embedded;
- no provider credential is embedded;
- no raw backend filesystem path is exposed;
- no CRM/calendar/email mutation control is exposed to the visitor;
- follow-up operations remain review-first.

## Production handoff

For the live AI Solo Company website, embed the same widget attributes in the website footer or WordPress chatbot plugin settings. Keep `data-lead-forms-enabled="false"` unless lead forms are intentionally re-enabled.
