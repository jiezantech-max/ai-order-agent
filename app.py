"""
AI Order Agent — chat to buy with PayPal sandbox + an LLM agent.

Mock mode (no credentials): fake PayPal responses + rule-based NLU, so the
whole flow can be tested without any keys.
"""
import json
import os
import re
import uuid
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()

app = Flask(__name__)

PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID", "")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "").rstrip("/")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-chat")

MOCK_PAYPAL = not (PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET)
MOCK_LLM = not (LLM_BASE_URL and LLM_API_KEY)

PAYPAL_API = "https://api-m.sandbox.paypal.com"

with open(os.path.join(os.path.dirname(__file__), "catalog.json"),
          encoding="utf-8") as f:
    CATALOG = json.load(f)

ORDERS = {}
LAST_ORDER_ID = None


def log(*a):
    print(datetime.now(timezone.utc).isoformat(), *a, flush=True)


def oid_short():
    return uuid.uuid4().hex[:8].upper()


# ---------------- PayPal client (sandbox) ----------------

def paypal_token():
    if MOCK_PAYPAL:
        return "mock-token"
    r = requests.post(
        PAYPAL_API + "/v1/oauth2/token",
        auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET),
        data={"grant_type": "client_credentials"},
        headers={"Accept": "application/json"},
        timeout=20,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def paypal_create_order(items, total):
    """Create order, return (order_id, approve_url)."""
    if MOCK_PAYPAL:
        oid = "MOCK-" + uuid.uuid4().hex[:8].upper()
        ORDERS[oid] = {"id": oid, "items": items, "total": total,
                       "status": "CREATED", "mock": True}
        return oid, "/mock-approve/" + oid
    token = paypal_token()
    line_items = []
    for it in items:
        line_items.append({
            "name": it["name_en"],
            "unit_amount": {"currency_code": "USD",
                            "value": "%.2f" % it["price"]},
            "quantity": str(it["qty"]),
        })
    payload = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "reference_id": oid_short(),
            "description": "AI Order Agent demo purchase",
            "amount": {
                "currency_code": "USD",
                "value": "%.2f" % total,
                "breakdown": {
                    "item_total": {"currency_code": "USD",
                                   "value": "%.2f" % total}
                },
            },
            "items": line_items,
        }],
        "application_context": {
            "brand_name": "AI Order Agent",
            "user_action": "PAY_NOW",
        },
    }
    r = requests.post(
        PAYPAL_API + "/v2/checkout/orders",
        json=payload,
        headers={"Authorization": "Bearer " + token,
                 "Content-Type": "application/json"},
        timeout=20,
    )
    r.raise_for_status()
    data = r.json()
    approve = ""
    for link in data["links"]:
        if link["rel"] == "approve":
            approve = link["href"]
    ORDERS[data["id"]] = {"id": data["id"], "items": items,
                          "total": total, "status": "CREATED",
                          "mock": False}
    return data["id"], approve


def paypal_capture(order_id):
    order = ORDERS.get(order_id, {})
    if order.get("mock"):
        cap_id = "MOCKCAP-" + uuid.uuid4().hex[:8].upper()
        order["status"] = "COMPLETED"
        order["capture_id"] = cap_id
        return {"id": cap_id, "status": "COMPLETED"}
    token = paypal_token()
    r = requests.post(
        PAYPAL_API + "/v2/checkout/orders/" + order_id + "/capture",
        headers={"Authorization": "Bearer " + token,
                 "Content-Type": "application/json"},
        timeout=20,
    )
    r.raise_for_status()
    data = r.json()
    cap = data["purchase_units"][0]["payments"]["captures"][0]
    order["status"] = data.get("status", "COMPLETED")
    order["capture_id"] = cap["id"]
    return {"id": cap["id"], "status": cap["status"]}


def paypal_refund(order_id):
    order = ORDERS.get(order_id)
    if not order or not order.get("capture_id"):
        raise ValueError("no captured payment for this order")
    if order.get("mock"):
        order["status"] = "REFUNDED"
        return {"status": "COMPLETED"}
    token = paypal_token()
    r = requests.post(
        PAYPAL_API + "/v2/payments/captures/"
        + order["capture_id"] + "/refund",
        headers={"Authorization": "Bearer " + token,
                 "Content-Type": "application/json"},
        timeout=20,
    )
    r.raise_for_status()
    order["status"] = "REFUNDED"
    return r.json()


# ---------------- LLM / NLU ----------------

def system_prompt():
    lines = []
    for p in CATALOG:
        lines.append("  %s: %s, $%s" % (p["id"], p["name_en"], p["price"]))
    return (
        "You are the order-taking AI for a small demo store.\n"
        "Parse the user message into JSON with keys:\n"
        '  intent: "buy" | "refund" | "status" | "menu" | "chat"\n'
        '  items: list of {"id": <catalog id>, "qty": <int>} for buy\n'
        '  target: "last" for refund/status (optional)\n'
        "Catalog (id: name_en, price USD):\n"
        + "\n".join(lines)
        + "\nReply with ONLY the JSON object, no other text."
    )


def llm_parse_intent(text):
    if MOCK_LLM:
        return mock_parse_intent(text)
    r = requests.post(
        LLM_BASE_URL + "/chat/completions",
        headers={"Authorization": "Bearer " + LLM_API_KEY,
                 "Content-Type": "application/json"},
        json={
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt()},
                {"role": "user", "content": text},
            ],
            "temperature": 0,
        },
        timeout=30,
    )
    r.raise_for_status()
    content = r.json()["choices"][0]["message"]["content"]
    m = re.search(r"\{.*\}", content, re.S)
    return json.loads(m.group(0))


CN_NUM = {"一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5,
             "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}


def cn_qty(text):
    m = re.search(r"(\d+)\s*(?:杯|个|份|瓶|包)?", text)
    if m:
        return int(m.group(1))
    m = re.search(r"([一二两三四五六七八九十])\s*(?:杯|个|份|瓶|包)?", text)
    if m:
        return CN_NUM[m.group(1)]
    return 1


def mock_parse_intent(text):
    t = text.lower()
    if any(w in t for w in ["refund", "退款"]):
        return {"intent": "refund", "target": "last"}
    if any(w in t for w in ["status", "状态", "订单"]):
        return {"intent": "status", "target": "last"}
    if any(w in t for w in ["menu", "菜单", "有什么"]):
        return {"intent": "menu"}
    items = []
    for p in CATALOG:
        keywords = [p["id"], p["name_en"].lower()] + p["name"].split()
        hit = any(k and (k in t or k in text) for k in keywords)
        if not hit:
            continue
        items.append({"id": p["id"], "qty": cn_qty(text)})
    if items:
        return {"intent": "buy", "items": items}
    return {"intent": "chat"}


def catalog_lookup(item_id):
    for p in CATALOG:
        if p["id"] == item_id:
            return p
    return None


# ---------------- agent ----------------

def agent_reply(text):
    global LAST_ORDER_ID
    try:
        intent = llm_parse_intent(text)
    except Exception as e:
        log("LLM parse failed:", e)
        return ("抱歉，我没理解。试试说“买两杯拿铁”或“看菜单”。", {})
    kind = intent.get("intent", "chat")
    if kind == "menu":
        return agent_menu()
    if kind == "buy":
        return agent_buy(intent)
    if kind == "status":
        return agent_status()
    if kind == "refund":
        return agent_refund()
    hint = "、".join(p["name"] for p in CATALOG[:3])
    reply = "你好！我是 AI 下单助手。" + "说“买两杯拿铁”我就帮你下单走 PayPal；本店有%s等，说“看菜单”看全部。" % hint
    return reply, {}


def agent_menu():
    lines = []
    for p in CATALOG:
        lines.append("- %s：$%s" % (p["name"], p["price"]))
    reply = "本店菜单：\n" + "\n".join(lines)
    reply += "\n直接说“买两杯拿铁”我就下单。"
    return reply, {}


def agent_buy(intent):
    global LAST_ORDER_ID
    items = []
    for it in intent.get("items", []):
        p = catalog_lookup(it["id"])
        if not p:
            continue
        qty = it.get("qty", 1)
        try:
            qty = max(1, int(qty))
        except (TypeError, ValueError):
            qty = 1
        item = dict(p)
        item["qty"] = qty
        items.append(item)
    if not items:
        return ("没找到这个商品，看下菜单再点吧。", {})
    total = 0.0
    for p in items:
        total += p["price"] * p["qty"]
    order_id, approve_url = paypal_create_order(items, total)
    LAST_ORDER_ID = order_id
    desc = "、".join("%sx%s" % (p["qty"], p["name"]) for p in items)
    if MOCK_PAYPAL:
        note = ""
    else:
        note = "请点击下面的 PayPal 链接完成付款（沙箱买家账号），再点“我已付款”。"
    reply = "好的：%s，共 $%.2f。\n订单已创建（%s）。%s" % (desc, total, order_id, note)
    return reply, {"order_id": order_id, "approve_url": approve_url, "mock": MOCK_PAYPAL}


def agent_status():
    oid = LAST_ORDER_ID
    if not oid or oid not in ORDERS:
        return ("还没有订单记录。", {})
    o = ORDERS[oid]
    reply = "最近订单 %s：状态 %s，金额 $%.2f。" % (oid, o["status"], o["total"])
    return reply, {"order_id": oid}


def agent_refund():
    oid = LAST_ORDER_ID
    if not oid or oid not in ORDERS:
        return ("没有可退款的订单。", {})
    o = ORDERS[oid]
    if o["status"]!= "COMPLETED":
        reply = "订单 %s 还没付款成功（状态 %s），无法退款。" % (oid, o["status"])
        return reply, {"order_id": oid}
    try:
        paypal_refund(oid)
    except Exception as e:
        log("refund failed:", e)
        return ("退款失败：%s" % e, {"order_id": oid})
    reply = "已为订单 %s 发起退款 $%.2f，款项将退回沙箱买家账户。" % (oid, o["total"])
    return reply, {"order_id": oid}


# ---------------- routes ----------------

@app.get("/")
def index():
    return render_template("index.html", mock_paypal=MOCK_PAYPAL, mock_llm=MOCK_LLM)


@app.post("/api/chat")
def chat():
    data = request.get_json(force=True)
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"reply": "说点什么吧，比如“买两杯拿铁”。"})
    reply, extra = agent_reply(text)
    out = {"reply": reply}
    out.update(extra)
    return jsonify(out)


@app.post("/api/capture")
def capture():
    data = request.get_json(force=True)
    order_id = data.get("order_id", "")
    if order_id not in ORDERS:
        return jsonify({"ok": False, "error": "unknown order"}), 400
    try:
        cap = paypal_capture(order_id)
    except Exception as e:
        log("capture failed:", e)
        return jsonify({"ok": False, "error": str(e)}), 502
    o = ORDERS[order_id]
    reply = "付款成功！订单 %s 已收款 $%.2f。说“退款”可退款。" % (order_id, o["total"])
    return jsonify({"ok": True, "order_id": order_id, "status": o["status"],
        "capture_id": cap["id"], "total": o["total"], "reply": reply})


@app.get("/api/catalog")
def catalog():
    return jsonify(CATALOG)


@app.get("/mock-approve/<order_id>")
def mock_approve(order_id):
    return render_template("mock_approve.html", order_id=order_id)


if __name__ == "__main__":
    mode = "MOCK" if (MOCK_PAYPAL or MOCK_LLM) else "LIVE"
    log("starting in %s mode" % mode)
    app.run(host="127.0.0.1", port=int(os.getenv("FLASK_PORT", 5000)), debug=False)
