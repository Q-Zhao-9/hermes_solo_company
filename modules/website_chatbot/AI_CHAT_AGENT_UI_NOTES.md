# UI Notes Learned from Existing AI Chat Agent

Inspected implementation path:

```text
/mnt/f/ai_chat_agent3/ai_chat_agent3/chat-frontend/chatgpt-webapp-devai/dist/chat.js
/mnt/f/ai_chat_agent3/ai_chat_agent3/backend/easiio-chatgpt-devai/src/models/Sfbot.ts
/mnt/f/ai_chat_agent3/ai_chat_agent3/frontend/easiio-sf-devai/src/pages/settings/ChatAIWidgetSetting.vue
```

The user mentioned `ai_chat_agent2`; this exact folder was not found. The closest active earlier implementation found was `ai_chat_agent3` under the F: drive, which contains the website chatbot browser widget behavior.

## Existing Embed Pattern

The existing system loads a browser widget script and then configures it through `window.chatlayer.set(...)`:

```html
<script src="https://chatbot.easiiodev.ai/chat.js"></script>
<script>
  window.chatlayer.set({
    uuid: "BOT_UUID",
    email: "",
    phone: "",
    language: "en"
  })
  window.chatlayer.show()
</script>
```

Important reusable ideas:

- A global controller object: `window.chatlayer`.
- Public methods: `set()`, `show()`, `open()`, `min()`, `max()`, `close()`.
- Widget settings fetched from backend by UUID.
- Chat UI rendered in an iframe.
- Floating capsule rendered directly in the host page.

## UI Patterns to Reuse

### 1. Floating capsule

The existing widget creates a fixed `.sfchat-capsule` with:

- Chat button.
- Red unread dot.
- Optional email button.
- Optional phone button.
- Optional WhatsApp/WeChat QR code button.
- Hover tooltips for chat/email/phone/QR.
- Pulse animation around the chat button.

Recommended for new version:

- Keep a bottom-right floating button/capsule.
- Use a red unread dot for first greeting or new bot message.
- Keep optional quick contact actions: email, phone, WhatsApp/QR.
- Prefer a simplified capsule by default: one round avatar button + optional quick actions hidden behind hover/click.

### 2. Avatar-as-floating-tool mode

Existing code supports using the bot avatar itself as the floating launcher:

- `useAvatarAsFloatingTool`
- `iconSize`: `small`, `medium`, `large`
- Avatar can be image or video.
- Optional overlay text/icon using `chatIconSetting.floatingText` and `floatingIcon`.
- Optional click-through link via `chatIconSetting.floatingLink`.

Recommended for new version:

- Support launcher styles:
  - `bubble` default round chat icon.
  - `avatar` image avatar.
  - `video-avatar` only later if needed.
- Support `launcherSize`: `small | medium | large`.
- Support `launcherText`: e.g. “Ask AI” or “Need help?”
- Support `launcherLink` only as optional advanced behavior.

### 3. Popup chat panel with iframe shell

Existing widget creates `.sflow-chat-plugin`:

- Fixed panel near bottom-right.
- Header title bar with avatar and bot name.
- Iframe content area.
- Minimize/maximize/close controls.
- Default size about `360px x 607px`.
- Small layout option using viewport-relative dimensions.
- Mobile CSS: panel width `80%`, left `10%`, height `70vh`.

Recommended for new version:

- Keep panel size close to existing behavior:
  - Desktop default: `360px x 607px` or `380px x 620px`.
  - Mobile: bottom sheet style, `calc(100vw - 24px)` x `70vh` or full height if needed.
- Start without iframe if we build the chat UI directly in widget JS.
- Use iframe only if we need isolation or a separate full chat app later.
- Keep minimize and close. Hide maximize initially unless needed.

### 4. Auto popup

Existing settings:

- `chatAiComponentsAutoPupop`
- `chatAiComponentsAutoPupopTime`
- Disabled on mobile.

Recommended for new version:

- Add `autoOpen`: boolean.
- Add `autoOpenDelaySeconds`: default `0` or `5`.
- Never auto-open on mobile by default.
- Only auto-open once per session using `sessionStorage`.

### 5. Greeting animation bubbles

Existing code supports animated greeting bubble list:

- `enableChatAiWidgetAnimation`
- `chatAiWidgetAnimationGreeting`: JSON array of greeting items.
- Greeting messages appear beside floating launcher after delay.
- Messages rotate/fade with show count limit.
- Optional avatar icon near greeting list.

Recommended for new version:

- Add a simpler proactive greeting bubble:
  - “Hi, I can help with AI automation or book a demo.”
  - Optional second line: “Ask me anything.”
- Support multiple greeting messages later.
- Respect `showGreetingBubble`, `greetingDelaySeconds`, `greetingShowTimes`.
- Hide greeting when user opens chat.

### 6. Page targeting / ignore pages

Existing setting:

- `floatToolIgnoresPages`: JSON list matched against `window.location.pathname`.

Recommended for new version:

- Add config:
  - `includePaths`
  - `excludePaths`
- For WordPress plugin, add page include/exclude settings later.
- For v1, support script data attributes:
  - `data-exclude-paths="/admin,/checkout"`

### 7. Contact form and leave-message features

Existing model contains:

- `enableChatAiContactForm`
- `chatAiContactForm`
- `leaveMessageType`
- `leaveMessageCount`
- `leaveMessageToEmail`
- `contactEmail`
- `contactPhone`
- `chatAiContactWxQrcode`

Recommended for CRM chatbot:

- Lead form should be first-class because it maps to Solo CRM:
  - name
  - email
  - company
  - phone
  - message
- Trigger the form when:
  - visitor asks for demo/pricing/contact/sales
  - bot cannot answer
  - visitor clicks “Contact sales” quick action
- On submit:
  - create/update CRM contact
  - create CRM deal for sales intent
  - add CRM activity with source page and transcript summary

### 8. Branding settings

Existing model supports:

- `chatAiName`
- `chatAiAvatarUrl`
- `chatAiTitleColor`
- `botTitle`
- `botHeaderBg`
- `botMainBg`
- `chatAIwidgetStyleSize`
- `language`

Recommended for new version:

- Use config object:

```json
{
  "title": "Easiio Assistant",
  "avatarUrl": "...",
  "primaryColor": "#2563eb",
  "language": "en",
  "panelSize": "standard",
  "launcherStyle": "avatar",
  "launcherSize": "small"
}
```

### 9. Backend settings by bot ID/site ID

Existing widget fetches settings by UUID through GraphQL.

Recommended for new version:

- Fetch public widget settings by `site_id` or `bot_id`:

```text
GET /api/widget/config?site_id=easiio-main
```

- The script data attributes should override backend defaults.
- Avoid exposing secrets in config response.

## Features to Add to the New Plan

Priority v1:

1. Single script embed.
2. `window.EasiioChatbot` controller with `set/open/close/minimize/show`.
3. Floating launcher with unread dot.
4. Popup chat panel.
5. Proactive greeting bubble.
6. Desktop/mobile responsive behavior.
7. Lead form inside chat.
8. CRM lead capture on email/demo/pricing intent.
9. Optional email/phone quick action buttons.
10. Page include/exclude paths.

Priority v2:

1. Avatar/video launcher.
2. Multiple rotating greeting bubbles.
3. Maximize panel.
4. QR code quick contact.
5. Widget admin settings UI.
6. Transcript storage.
7. Full iframe chat app mode.

## Things Not to Copy Directly

- Do not hard-code environment URLs like `https://chatbot.easiiodev.ai` or `http://localhost:7010/api`.
- Do not require a second inline script if data attributes can initialize the widget.
- Do not expose `request_token`, API keys, or CRM details to the browser.
- Do not rely on global function names like `navToChatFloatPage`; keep globals under one namespace.
- Do not auto-open on mobile.
- Avoid huge z-index values unless necessary; use consistent widget z-index like `2147483000`.
