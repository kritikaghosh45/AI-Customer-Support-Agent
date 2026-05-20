
# 🛍️ AI Customer Support Agent for Commerce

A Python-based AI customer support chatbot for e-commerce, powered by **Google Gemini (Free)** and built with a **Streamlit** web UI.

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
AI-Customer-Support-Agent/
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

### 2. Get your FREE Gemini API key

1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Sign in with your Google account
3. Click **Get API Key** → **Create API key**
4. Copy the key (starts with `AIza...`)


### 3. Run the app

```bash
python -m streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser and paste your Gemini API key in the sidebar.

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
- `"I'm really frustrated — my order ORD-1002 has been stuck for days"`

---

## 🔧 How It Works

The agent uses **Gemini's function calling (tool use)** feature:

1. User sends a message
2. Gemini decides which tool(s) to call
3. Tools query the mock commerce database
4. Gemini receives the data and crafts a helpful response

### Tools available to the agent:

| Tool | What it does |
|------|-------------|
| `track_order` | Fetches order details by ID |
| `initiate_return` | Creates a return request |
| `get_product_info` | Looks up product data |
| `get_return_policy` | Returns policy details |
| `file_complaint` | Creates a complaint ticket |

---

## 🔄 Extending the Project

- **Real database**: Replace mock dicts with actual DB queries (SQLite/PostgreSQL)
- **Authentication**: Add customer login before showing order data
- **Email notifications**: Send return/complaint confirmations via email
- **Deploy online**: Host for free on [Streamlit Cloud](https://streamlit.io/cloud)
