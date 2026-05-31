# AI Solo Company Voice Chatbot Integration Lesson

Use this reference when adding voice-call functionality to the existing Easiio website chatbot and when embedding the result on WordPress/easiiodev.ai.

## Reusable approach

1. Add the voice-call entry inside the existing chatbot widget instead of creating a separate floating voice button.
   - Main widget file: `/home/jianl/.hermes/tools/website_chatbot/widget/widget.js`
   - Expose configuration via script data attributes such as:
     - `data-voice-call-enabled="true"`
     - `data-voice-call-label="Start voice call"`
     - `data-api-base="...chatbot-api..."`
     - `data-voice-call-api-base="...voice-api..."`
   - Treat voice-call buttons as explicit controls, not text quick-action prompt buttons.

2. Create a static website-style demo page first.
   - Example file: `/home/jianl/.hermes/tools/website_chatbot/widget/ai-solo-company-voice-chatbot.html`
   - Demo should load the chatbot widget and point it at the chatbot API and voice-call API preview URLs.

3. Serve three pieces through Hermes Proxy/Sitelet-style review URLs before production embedding:
   - static demo website
   - chatbot API
   - voice-call API

4. Verify both APIs independently before UI testing:
   - chatbot API `/health`
   - voice-call API `/health`
   - voice-call session creation
   - chatbot session creation

5. Run the local verification set:
   - from `/home/jianl/.hermes/tools/website_chatbot`:
     - `node --check widget/widget.js`
     - `node tests/widget_static.test.js`
     - `python3 tests/test_backend.py -v`
   - from `/home/jianl/.hermes/tools/voice_call_bot`:
     - `python3 tests/test_voice_call_bot.py -v`
   - run a changed-files secret scan.

## WordPress embedding lesson

Do not rely on inline `<script>` or `<iframe>` blocks inside WordPress page content for the live easiiodev.ai site. During the voice-chatbot integration, WordPress stripped inline script/iframe content from page body updates. The safe fallback was to add a normal homepage content section linking to the working Hermes Proxy demo.

For a production floating chatbot on WordPress, use one of these paths instead:

1. the existing WordPress chatbot plugin/footer injection path,
2. a theme/footer injection path,
3. a controlled shortcode/block that enqueues scripts properly,
4. or a plugin setting that loads the widget globally or on selected pages.

Avoid raw executable scripts in ordinary page body content.