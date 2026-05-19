import anthropic
import json
from datetime import datetime, timedelta
import random

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
        "description": "Lightweight and breathable running shoes with cushioned sole. Available in sizes 6–13.",
        "warranty": "6 months", "return_window_days": 60,
    },
    "coffee-maker": {
        "name": "Coffee Maker", "price": 49.99, "in_stock": False,
        "description": "12-cup programmable coffee maker with auto shut-off and brew-strength control.",
        "warranty": "2 years", "return_window_days": 30,
    },
    "bluetooth-speaker": {
        "name": "Bluetooth Speaker", "price": 59.99, "in_stock": True,
        "description": "Portable waterproof speaker with 360° sound and 12-hour playtime.",
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
        "(2) We'll email a prepaid return label within 24 hours. "
        "(3) Drop off the package at any courier location. "
        "(4) Refund is processed within 5–7 business days after we receive the item."
    ),
}

COMPLAINT_TICKETS = {}

# ─────────────────────────────────────────────
# Tool Definitions
# ─────────────────────────────────────────────

TOOLS = [
    {
        "name": "track_order",
        "description": (
            "Look up the status, items, tracking number, and estimated delivery "
            "of a customer order using the order ID."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order ID, e.g. ORD-1001",
                }
            },
            "required": ["order_id"],
        },
    },
    {
        "name": "initiate_return",
        "description": (
            "Initiate a return or refund request for a delivered order. "
            "Returns a confirmation number and next steps."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order ID to return",
                },
                "reason": {
                    "type": "string",
                    "description": "The reason for the return (e.g. defective, wrong item, changed mind)",
                },
            },
            "required": ["order_id", "reason"],
        },
    },
    {
        "name": "get_product_info",
        "description": (
            "Retrieve details about a product including price, stock availability, "
            "description, warranty, and return window."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "product_name": {
                    "type": "string",
                    "description": "Product name or keyword to search (e.g. 'headphones', 'coffee maker')",
                }
            },
            "required": ["product_name"],
        },
    },
    {
        "name": "get_return_policy",
        "description": "Get the store's return and refund policy details.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Specific question about the return policy (optional)",
                }
            },
            "required": [],
        },
    },
    {
        "name": "file_complaint",
        "description": (
            "File a formal complaint or escalation ticket on behalf of the customer. "
            "Use this for serious issues like damaged items, billing errors, or repeated problems."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_name": {
                    "type": "string",
                    "description": "Customer's name",
                },
                "issue_description": {
                    "type": "string",
                    "description": "Detailed description of the complaint",
                },
                "order_id": {
                    "type": "string",
                    "description": "Related order ID if applicable",
                },
            },
            "required": ["customer_name", "issue_description"],
        },
    },
]


# ─────────────────────────────────────────────
# Tool Execution Logic
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
    if order["status"] not in ("delivered",):
        return {
            "error": f"Order '{order_id}' cannot be returned — current status is '{order['status']}'. "
                     "Only delivered orders are eligible for returns."
        }
    ref = f"RET-{random.randint(10000, 99999)}"
    return {
        "return_reference": ref,
        "order_id": order_id,
        "reason": reason,
        "status": "initiated",
        "next_steps": RETURN_POLICIES["process"],
        "refund_eta": "5–7 business days after item is received",
    }


def get_product_info(product_name: str) -> dict:
    keyword = product_name.lower().replace(" ", "-")
    # Try exact match first
    for key, product in MOCK_PRODUCTS.items():
        if keyword in key or any(word in key for word in keyword.split("-")):
            return product
    # Try partial name match
    for key, product in MOCK_PRODUCTS.items():
        if any(word in product["name"].lower() for word in product_name.lower().split()):
            return product
    return {
        "error": f"No product found matching '{product_name}'. "
                 "Available products: Wireless Headphones, Running Shoes, Coffee Maker, Bluetooth Speaker, Sports Socks."
    }


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
        "ticket_id": ticket_id,
        "customer_name": customer_name,
        "issue": issue_description,
        "order_id": order_id,
        "status": "open",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "assigned_to": "Support Team",
    }
    return {
        "ticket_id": ticket_id,
        "message": f"Your complaint has been filed. Ticket ID: {ticket_id}.",
        "response_time": "A support agent will contact you within 24 hours.",
        "status": "open",
    }


def execute_tool(tool_name: str, tool_input: dict) -> str:
    try:
        if tool_name == "track_order":
            result = track_order(**tool_input)
        elif tool_name == "initiate_return":
            result = initiate_return(**tool_input)
        elif tool_name == "get_product_info":
            result = get_product_info(**tool_input)
        elif tool_name == "get_return_policy":
            result = get_return_policy(**tool_input)
        elif tool_name == "file_complaint":
            result = file_complaint(**tool_input)
        else:
            result = {"error": f"Unknown tool: {tool_name}"}
    except Exception as e:
        result = {"error": str(e)}
    return json.dumps(result, indent=2)


# ─────────────────────────────────────────────
# Agent Core
# ─────────────────────────────────────────────

SYSTEM_PROMPT = """You are a friendly and professional AI Customer Support Agent for ShopEase, an online commerce store.

Your job is to help customers with:
- **Order Tracking**: Look up order status, estimated delivery, and tracking numbers.
- **Returns & Refunds**: Initiate return requests and explain the refund process.
- **Product Q&A**: Answer questions about products, availability, pricing, and warranty.
- **Complaints & Escalation**: File formal complaint tickets for serious issues and ensure the customer feels heard.

Guidelines:
- Always be empathetic, patient, and solution-focused.
- Use the available tools to fetch real data — don't make up order details.
- If a customer seems frustrated, acknowledge their feelings before jumping to solutions.
- For complaints, always file a ticket using the file_complaint tool.
- Keep responses clear and concise — avoid overly long replies.
- If you don't know something, say so honestly and offer to escalate.

Sample order IDs for demo: ORD-1001 (shipped), ORD-1002 (processing), ORD-1003 (delivered), ORD-1004 (cancelled)"""


class CommerceAgent:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.conversation_history = []

    def reset(self):
        self.conversation_history = []

    def chat(self, user_message: str) -> str:
        self.conversation_history.append({"role": "user", "content": user_message})

        while True:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=self.conversation_history,
            )

            # If Claude wants to use a tool
            if response.stop_reason == "tool_use":
                # Add Claude's response (with tool_use blocks) to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response.content,
                })

                # Execute each tool and collect results
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        tool_output = execute_tool(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": tool_output,
                        })

                # Add tool results to history and loop back
                self.conversation_history.append({
                    "role": "user",
                    "content": tool_results,
                })

            else:
                # Final text response
                final_text = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        final_text += block.text

                self.conversation_history.append({
                    "role": "assistant",
                    "content": final_text,
                })
                return final_text
