# Nebius × NVIDIA Global AI Hackathon — 双投参赛指南

投稿页：https://nebiusglobalaihackathon.devpost.com/
投稿截止：**2026-10-31 01:00（北京时间）** | 评审 12 月 1–15 日 | 约 2027-01-11 公布

## 双投架构（一套代码，两个参赛）

AI 下单助手本身是"PayPal 支付 + AI 对话"的应用。Nebius 赛道要求"用 NVIDIA
开源模型 + 跑在 Nebius Token Factory / AI Cloud 上"。Token Factory 的 API
是 OpenAI 兼容的，咱们 agent 的 LLM 层本来就是 `LLM_BASE_URL` /
`LLM_API_KEY` / `LLM_MODEL` 三件套——**换三个环境变量就等于换了大脑**，
从 Nemotron 的视角看，这是一个"跑在 Token Factory 上、由 Nemotron 驱动
的智能下单 agent"。PayPal 沙箱部分完全不动。

推荐赛道：**Best Apps & Agents**（"powered by Nemotron on Token Factory"
的实用 app/agent）。

## Johnny 要做的（账号/绑卡，只能他自己）

1. 去 Token Factory 官网注册账号，完成 onboarding：
   创建 billing account 并**绑定一张银行卡**（Visa/Mastercard 这类能做国际
   扣款的卡；文档明确"扣费失败会暂停账号"，绑一张长期有效的卡）。
2. 注册送 **$1 试用额度（30 天有效）**。绑卡≠花钱：只有当余额为负或达到
   计费阈值时才从卡扣费，用量控制在 $1 以内不会产生扣费。
3. 在控制台创建一个 **API key**，自己复制下来。
4. `cp .env.nebius.example .env`，填入 key 和在 playground 里挑好的
   Nemotron 模型 ID，`python app.py` 跑一遍下单→付款→退款全链路。

费用估算：一次对话调用约几千 token；按 Nemotron 级别约 $0.06–$2/百万
token 算，几十次演示调用也花不到 $1 的零头。

## 投稿材料对照（和 PayPal 几乎同套）

| 材料 | Nebius 要求 | 状态 |
|---|---|---|
| 可运行项目 | 跑在 Token Factory/AI Cloud + 至少 1 个 NVIDIA 开源模型 | 待他本地实测 |
| 公开代码仓 + 开源 License | 已有 MIT LICENSE，需推到 GitHub 公开 | 待推送 |
| 演示视频 ≤3 分钟 | 必须体现 Nemotron/Token Factory 驱动（可和 PayPal 版共用素材，另剪一版） | 待实测后录制 |
| 项目描述 | 讲清楚"Nemotron 驱动的下单 agent" | 待写 |

评审：先过"赛道契合 + 真用了 Nebius/NVIDIA 工具"的硬门槛，再按技术实现 /
设计 / 潜在影响 / 创意四项等权重打分。

奖金：冠军 $20,000 / 亚军 $10,000 / 季军 $6,000；每个赛道冠军 NVIDIA
Jetson Orin Nano；Best Use of Tavily $3,000。**大陆不在官方排除名单**，
但有当地法律兜底条款；奖金到国内银行是否顺畅未验证。
