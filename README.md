# 🛍️ AI Customer Support Agent for Commerce

A Python-based AI customer support chatbot for e-commerce, powered by **Anthropic Claude** and built with a **Streamlit** web UI.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📦 Order Tracking | Look up order status, delivery date & tracking number |
| ↩️ Returns & Refunds | Initiate return requests and get refund timelines |
| 🔍 Product Q&A | Get product details, pricing, stock & warranty info |
| 🎫 Complaints & Escalation | File formal complaint tickets with reference IDs |

---

## 🏗️ Project Structure

```
ai_commerce_support/
├── agent.py          # Core agent logic, tools, and mock database
├── app.py            # Streamlit web UI
├── requirements.txt  # Dependencies
└── README.md
```

---

## 🚀 Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Get your Anthropic API key

Sign up at [console.anthropic.com](https://console.anthropic.com) and create an API key.

### 3. Run the app

```bash
streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser and enter your API key in the sidebar.

---

## 🧪 Demo Data

Use these order IDs to test the agent:

| Order ID | Status | Customer |
|----------|--------|----------|
| ORD-1001 | Shipped | Alice Johnson |
| ORD-1002 | Processing | Bob Smith |
| ORD-1003 | Delivered ✅ | Carol White |
| ORD-1004 | Cancelled | David Lee |

### Try these prompts:
- `"Where is my order ORD-1001?"`
- `"I want to return my order ORD-1003, it was defective"`
- `"Tell me about the Wireless Headphones"`
- `"What is your return policy?"`
- `"I'm really frustrated — my order ORD-1002 has been stuck for days"` *(triggers complaint escalation)*

---

## 🔧 How It Works

The agent uses **Claude's tool use (function calling)** feature:

1. User sends a message
2. Claude decides which tool(s) to call
3. Tools query the mock commerce database
4. Claude receives the data and crafts a helpful response

### Tools available to Claude:

| Tool | What it does |
|------|-------------|
| `track_order` | Fetches order details by ID |
| `initiate_return` | Creates a return request |
| `get_product_info` | Looks up product data |
| `get_return_policy` | Returns policy details |
| `file_complaint` | Creates a complaint ticket |

---

## 🔄 Extending the Project

- **Real database**: Replace `MOCK_ORDERS` / `MOCK_PRODUCTS` dicts with actual DB queries
- **Authentication**: Add customer login before showing order data
- **Email notifications**: Send return/complaint confirmations via email
- **Analytics**: Track common issues and resolution rates
