tools = [
    {
        "type": "function",
        "function": {
            "name": "check_order_status",
            "description": "Check the status of an order.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string"
                    }
                },
                "required": ["order_id"],
                "additionalProperties": False
            }
        }
    },
        {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "Search products by keyword.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string"
                    }
                },
                "required": ["keyword"],
                "additionalProperties": False
            }
        }
    },
        {
        "type": "function",
        "function": {
            "name": "cancel_order",
            "description": "Cancel an order if it is still processing.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string"
                    }
                },
                "required": ["order_id"],
                "additionalProperties": False
            }
        }
    },
        {
        "type": "function",
        "function": {
            "name": "check_refund_eligibility",
            "description": "Check if an order can receive a refund.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string"
                    }
                },
                "required": ["order_id"],
                "additionalProperties": False
            }
        }
    },
        {
        "type": "function",
        "function": {
            "name": "ticket_inquiry",
            "description": "Look up a support ticket.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "string"
                    }
                },
                "required": ["ticket_id"],
                "additionalProperties": False
            }
        }
    },
        {
        "type": "function",
        "function": {
            "name": "send_support_email",
            "description": "Send a support escalation email.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string"
                    },
                    "issue": {
                        "type": "string"
                    }
                },
                "required": [
                    "order_id",
                    "issue"
                ],
                "additionalProperties": False
            }
        }
    },
{
    "type": "function",
    "function": {
        "name": "search_knowledge_base",
        "description": "Search the company knowledge base for policies, warranties, shipping information, and FAQs.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string"
                }
            },
            "required": [
                "query"
            ],
            "additionalProperties": False
        }
    }
}
]