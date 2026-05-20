import json
from datetime import datetime, timedelta
import random
from google import genai
from google.genai import types

# ─────────────────────────────────────────────
# Mock Commerce Database
# ─────────────────────────────────────────────

MOCK_ORDERS = {
    "ORD-1001": {
        "id": "ORD-1001", "customer": "Alice Johnson",
        "items": [{"name": "Wireless Headphones", "qty": 1, "price": 79.99}],
        "total": 79.99, "status": "shipped",
        "estimated_delivery": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
        "tracking_number": "TRK-9988776655",
    },
    "ORD-1002": {
        "id": "ORD-1002", "customer": "Bob Smith",
        "items": [
            {"name": "Running Shoes", "qty": 1, "price": 120.00},
            {"name": "Sports Socks (3-pack)", "qty": 2, "price": 9.99},
        ],
        "total": 139.98, "status": "processing",
        "estimated_delivery": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
        "tracking_number": None,
    },
    "ORD-1003": {
        "id": "ORD-1003", "customer": "Carol White",
        "items": [{"name": "Coffee Maker", "qty": 1, "price": 49.99}],
        "total": 49.99, "status": "delivered",
        "estimated_delivery": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
        "tracking_number": "TRK-1122334455",
    },
    "ORD-1004": {
        "id": "ORD-1004", "customer": "David Lee",
        "items": [{"name": "Bluetooth Speaker", "qty": 1, "price": 59.99}],
        "total": 59.99, "status": "cancelled",
        "estimated_delivery": None,
        "tracking_number": None,
    },
}

MOCK_PRODUCTS = {
    "wireless-headphones": {
        "name": "Wireless Headphones", "price": 79.99, "in_stock": True,
        "description": "Premium over-ear headphones with 30-hour battery life and active noise cancellation.",
        "warranty": "1 year", "return_window_days": 30,
    },
    "running-shoes": {
        "name": "Running Shoes", "price": 120.00, "in_stock": True,
        "description": "Lightweight and breathable running shoes with cushioned sole. Available in sizes 6-13.",
        "warranty": "6 months", "return_window_days": 60,
    },
    "coffee-maker": {
        "name": "Coffee Maker", "price": 49.99, "in_stock": False,
        "description": "12-cup programmable coffee maker with auto shut-off and brew-strength control.",
        "warranty": "2 years", "return_window_days": 30,
    },
    "bluetooth-speaker": {
        "name": "Bluetooth Speaker", "price": 59.99, "in_stock": True,
        "description": "Portable waterproof speaker with 360 sound and 12-hour playtime.",
        "warranty": "1 year", "return_window_days": 30,
    },
    "sports-socks": {
        "name": "Sports Socks (3-pack)", "price": 9.99, "in_stock": True,
        "description": "Moisture-wicking athletic socks with arch support. One size fits most.",
        "warranty": "None", "return_window_days": 14,
    },
}

RETURN_POLICIES = {
    "standard": "Items can be returned within 30 days of delivery for a full refund.",
    "extended": "Running shoes have a 60-day return window.",
    "non_returnable": "Items marked as final sale or opened software cannot be returned.",
    "process": (
        "To initiate a return: (1) Contact support with your order ID. "
        "(2) We will email a prepaid return label within 24 hours. "
        "(3) Drop off the package at any courier location. "
        "(4) Refund is processed within 5-7 business days after we receive the item."
    ),
}

COMPLAINT_TICKETS = {}

# ─────────────────────────────────────────────
# Tool Functions
# ─────────────────────────────────────────────

def track_order(order_id: str) -> dict:
    order = MOCK_ORDERS.get(order_id.upper())
    if not order:
        return {"error": f"No order found with ID '{order_id}'. Please check the order ID and try again."}
    return order

def initiate_return(order_id: str, reason: str) -> dict:
    order = MOCK_ORDERS.get(order_id.upper())
    if not order:
        return {"error": f"Order '{order_id}' not found."}
    if order["status"] != "delivered":
        return {"error": f"Order '{order_id}' cannot be returned - current status is '{order['status']}'. Only delivered orders are eligible."}
    ref = f"RET-{random.randint(10000, 99999)}"
    return {
        "return_reference": ref, "order_id": order_id, "reason": reason,
        "status": "initiated", "next_steps": RETURN_POLICIES["process"],
        "refund_eta": "5-7 business days after item is received",
    }

def get_product_info(product_name: str) -> dict:
    keyword = product_name.lower().replace(" ", "-")
    for key, product in MOCK_PRODUCTS.items():
        if keyword in key or any(word in key for word in keyword.split("-")):
            return product
    for key, product in MOCK_PRODUCTS.items():
        if any(word in product["name"].lower() for word in product_name.lower().split()):
            return product
    return {"error": f"No product found matching '{product_name}'. Available: Wireless Headphones, Running Shoes, Coffee Maker, Bluetooth Speaker, Sports Socks."}

def get_return_policy(query: str = "") -> dict:
    return {
        "standard_policy": RETURN_POLICIES["standard"],
        "extended_policy": RETURN_POLICIES["extended"],
        "non_returnable": RETURN_POLICIES["non_returnable"],
        "return_process": RETURN_POLICIES["process"],
    }

def file_complaint(customer_name: str, issue_description: str, order_id: str = None) -> dict:
    ticket_id = f"TKT-{random.randint(100000, 999999)}"
    COMPLAINT_TICKETS[ticket_id] = {
        "ticket_id": ticket_id, "customer_name": customer_name,
        "issue": issue_description, "order_id": order_id, "status": "open",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    return {
        "ticket_id": ticket_id,
        "message": f"Complaint filed. Ticket ID: {ticket_id}.",
        "response_time": "A support agent will contact you within 24 hours.",
        "status": "open",
    }

TOOL_MAP = {
    "track_order": track_order,
    "initiate_return": initiate_return,
    "get_product_info": get_product_info,
    "get_return_policy": get_return_policy,
    "file_complaint": file_complaint,
}

# ─────────────────────────────────────────────
# Tool Declarations for new SDK
# ─────────────────────────────────────────────

TOOLS = [
    types.FunctionDeclaration(
        name="track_order",
        description="Look up the status, items, tracking number, and estimated delivery of a customer order.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={"order_id": types.Schema(type=types.Type.STRING, description="The order ID e.g. ORD-1001")},
            required=["order_id"],
        ),
    ),
    types.FunctionDeclaration(
        name="initiate_return",
        description="Initiate a return or refund request for a delivered order.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "order_id": types.Schema(type=types.Type.STRING, description="The order ID to return"),
                "reason": types.Schema(type=types.Type.STRING, description="The reason for the return"),
            },
            required=["order_id", "reason"],
        ),
    ),
    types.FunctionDeclaration(
        name="get_product_info",
        description="Retrieve product details including price, stock, description, warranty, and return window.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={"product_name": types.Schema(type=types.Type.STRING, description="Product name or keyword")},
            required=["product_name"],
        ),
    ),
    types.FunctionDeclaration(
        name="get_return_policy",
        description="Get the store's return and refund policy details.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={"query": types.Schema(type=types.Type.STRING, description="Optional question about policy")},
            required=[],
        ),
    ),
    types.FunctionDeclaration(
        name="file_complaint",
        description="File a formal complaint or escalation ticket on behalf of the customer.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "customer_name": types.Schema(type=types.Type.STRING, description="Customer's name"),
                "issue_description": types.Schema(type=types.Type.STRING, description="Description of the complaint"),
                "order_id": types.Schema(type=types.Type.STRING, description="Related order ID if applicable"),
            },
            required=["customer_name", "issue_description"],
        ),
    ),
]

SYSTEM_PROMPT = """You are a friendly and professional AI Customer Support Agent for ShopEase, an online commerce store.

Your job is to help customers with:
- Order Tracking: Look up order status, estimated delivery, and tracking numbers.
- Returns & Refunds: Initiate return requests and explain the refund process.
- Product Q&A: Answer questions about products, availability, pricing, and warranty.
- Complaints & Escalation: File formal complaint tickets for serious issues.

Guidelines:
- Always be empathetic, patient, and solution-focused.
- Use the available tools to fetch real data — don't make up order details.
- If a customer seems frustrated, acknowledge their feelings before jumping to solutions.
- For complaints, always file a ticket using the file_complaint tool.
- Keep responses clear and concise.

Sample order IDs for demo: ORD-1001 (shipped), ORD-1002 (processing), ORD-1003 (delivered), ORD-1004 (cancelled)"""


# ─────────────────────────────────────────────
# Agent Core
# ─────────────────────────────────────────────

class CommerceAgent:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.history = []
        self.tool_config = types.Tool(function_declarations=TOOLS)

    def reset(self):
        self.history = []

    def ask(self, user_message: str) -> str:
        self.history.append(types.Content(role="user", parts=[types.Part(text=user_message)]))

        while True:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-lite",
                contents=self.history,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    tools=[self.tool_config],
                ),
            )

            candidate = response.candidates[0]
            self.history.append(candidate.content)

            # Check for function calls
            function_calls = [p for p in candidate.content.parts if p.function_call]

            if function_calls:
                tool_results = []
                for part in function_calls:
                    fn = part.function_call
                    tool_fn = TOOL_MAP.get(fn.name)
                    args = dict(fn.args) if fn.args else {}
                    result = tool_fn(**args) if tool_fn else {"error": f"Unknown tool: {fn.name}"}
                    tool_results.append(
                        types.Part(function_response=types.FunctionResponse(
                            name=fn.name,
                            response={"result": json.dumps(result)},
                        ))
                    )
                self.history.append(types.Content(role="user", parts=tool_results))
            else:
                # Return final text
                return response.text
