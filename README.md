# AI Order Agent — PayPal AI Hackathon 2026

> 聊天下单：用自然语言买东西，AI 代理走 PayPal 完成下单、收款与退款。Chat to buy — an AI agent that takes natural-language orders and completes them via PayPal.

Chat to buy. An AI agent that takes natural-language orders ("buy me two lattes"),
creates a real PayPal (sandbox) order, walks the buyer through approval, captures
the payment, and handles refunds — all inside a chat window.

Built for the [PayPal AI Hackathon](https://paypalaihackathon.devpost.com/)
(deadline: Nov 12, 2026 12:00 PT).

## How it works

1. You type what you want in plain language (Chinese or English).
2. The AI agent parses your intent (buy / refund / order status) via an
   OpenAI-compatible chat model.
3. The agent creates a PayPal **sandbox** order and gives you an approval link.
4. You approve as the sandbox buyer; the agent captures the payment.
5. Say "refund my last order" and the agent refunds it via the PayPal API.

PayPal is at the core (real Orders v2 + Payments APIs on sandbox), AI drives the
whole interaction (NLU, confirmation summaries, refund reasoning).

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your SANDBOX credentials, never commit .env
python app.py
```

Open http://localhost:5000 and start chatting.

Without credentials the app runs in **mock mode** (fake PayPal + rule-based NLU)
so the UI and agent flow can be tested end to end.

## Configuration (.env)

| Key | Description |
|---|---|
| `PAYPAL_CLIENT_ID` / `PAYPAL_CLIENT_SECRET` | Sandbox REST app credentials from developer.paypal.com |
| `PAYPAL_MODE` | `sandbox` (never use live for this demo) |
| `LLM_BASE_URL` | OpenAI-compatible base URL (e.g. DeepSeek, OpenAI) |
| `LLM_API_KEY` | API key for the chat model |
| `LLM_MODEL` | Model name, e.g. `deepseek-chat` |

## Project layout

- `app.py` — Flask backend: chat API, agent loop, PayPal client
- `catalog.json` — demo store catalog (prices in USD)
- `templates/index.html` — chat UI
- `requirements.txt` — Python deps

## License

MIT — see LICENSE.
