# Demo Video Script — AI Order Agent, Nebius × NVIDIA cut (draft, < 3 min)

Target: ~2:40 at a calm pace. Same app as the PayPal entry, but the LLM is
NVIDIA Nemotron running on Nebius Token Factory (see `.env.nebius.example`).
Record the screen with the chat UI open; do the PayPal sandbox buyer approval
in a second window.

---

**[0:00–0:20] Hook**

> "Ordering online still means forms, carts, and checkouts.
> What if buying something was just… talking?
> This is AI Order Agent — and its brain is NVIDIA Nemotron,
> served from Nebius Token Factory."

*(show the .env: `LLM_BASE_URL=https://api.tokenfactory.nebius.com/v1`
and the Nemotron model ID — 5s)*

**[0:20–1:25] Live order**

> "Let me buy two lattes."
> *(type: buy two lattes — show the agent's reply with the order summary)*

> "Nemotron understood my intent, picked the items from the catalog,
> and created a real PayPal sandbox order — $9.00."
> *(show the PayPal approval link; click through to the sandbox buyer login)*

> "I approve as the sandbox buyer…"
> *(approve the payment in the PayPal sandbox window)*

> "…and the agent captures it."
> *(click "confirm receipt" in chat — show the success message)*

**[1:25–1:55] Refund**

> "Changed my mind? Just say so."
> *(type: refund my last order — show the refund confirmation)*

> "The agent refunds the captured payment through PayPal's API.
> Full buy–pay–refund loop, all in chat."

**[1:55–2:30] How it works**

> "Under the hood: NVIDIA Nemotron, called through Nebius Token Factory's
> OpenAI-compatible API, parses natural language into order intents —
> buy, refund, order status — in Chinese and English.
> PayPal's Orders v2 and Payments APIs do the money movement —
> create, approve, capture, refund — all on PayPal sandbox,
> so not a cent of real money is involved.
> One codebase, two hackathons: swap three environment variables
> and the agent's brain moves from DeepSeek to Nemotron."

**[2:30–2:40] Close**

> "AI Order Agent — chat to buy, powered by Nemotron on Nebius Token Factory.
> Built for the Nebius × NVIDIA Global AI Hackathon."

---

## Shot list

1. `.env` snippet: Token Factory base URL + Nemotron model ID (5s).
2. Chat UI full screen: "buy two lattes" → order created card with approval link.
3. PayPal sandbox approval page (buyer login → approve).
4. Back in chat: capture confirmation.
5. "refund my last order" → refund confirmation.
6. (Optional) one Chinese exchange, e.g. "买两杯拿铁" — shows Nemotron's
   multilingual NLU — 10s.

## Notes

- Keep the sandbox buyer logged in before recording to avoid login delays.
- If the approval step is slow, edit it down — the story is
  chat → approve → captured → refunded, powered by Nemotron.
- Revise after the real Nebius end-to-end test.
