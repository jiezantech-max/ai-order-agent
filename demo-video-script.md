# Demo Video Script — AI Order Agent (draft, < 3 min)

Target: ~2:30 at a calm pace. Record the screen with the chat UI open;
do the PayPal sandbox buyer approval in a second window.

---

**[0:00–0:15] Hook**

> "Ordering online still means forms, carts, and checkouts.
> What if buying something was just… talking?
> This is AI Order Agent — you chat, the AI handles PayPal."

**[0:15–1:15] Live order**

> "Let me buy two lattes."
> *(type: buy two lattes — show the agent's reply with the order summary)*

> "The agent understood my intent, picked the items from the catalog,
> and created a real PayPal sandbox order — $9.00."
> *(show the PayPal approval link; click through to the sandbox buyer login)*

> "I approve as the sandbox buyer…"
> *(approve the payment in the PayPal sandbox window)*

> "…and the agent captures it."
> *(click "confirm receipt" in chat — show the success message)*

**[1:15–1:45] Refund**

> "Changed my mind? Just say so."
> *(type: refund my last order — show the refund confirmation)*

> "The agent refunds the captured payment through PayPal's API.
> Full buy–pay–refund loop, all in chat."

**[1:45–2:20] How it works**

> "Under the hood: an LLM agent parses natural language into order intents,
> and PayPal's Orders v2 and Payments APIs do the money movement —
> create, approve, capture, refund — all on PayPal sandbox,
> so not a cent of real money is involved.
> This is agentic commerce: the AI doesn't just recommend,
> it completes the transaction."

**[2:20–2:30] Close**

> "AI Order Agent — chat to buy. Built for the PayPal AI Hackathon."

---

## Shot list

1. Chat UI full screen, menu question + answer (5s B-roll, optional).
2. Typing "buy two lattes" → order created card with approval link.
3. PayPal sandbox approval page (buyer login → approve).
4. Back in chat: capture confirmation.
5. "refund my last order" → refund confirmation.
6. (Optional) code walkthrough: `paypal_create_order` / `paypal_capture` /
   `paypal_refund` in `app.py` — 10s max.

## Notes

- Keep the sandbox buyer logged in before recording to avoid login delays.
- If the approval step is slow, edit it down — the story is
  chat → approve → captured → refunded.
- Revise after the real-sandbox end-to-end test.
