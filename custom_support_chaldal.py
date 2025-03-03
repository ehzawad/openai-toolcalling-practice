import os
import json
from openai import OpenAI
from pydantic import BaseModel, Field

# Initialize the OpenAI client (assumes OPENAI_API_KEY is set)
client = OpenAI()

################################################################################
# 1) Define Pydantic Models for Function Parameters
################################################################################

class GetUserParams(BaseModel):
    key: str = Field(..., description="The attribute to search for a user by (email, phone, or username).")
    value: str = Field(..., description="The value to match for the specified attribute.")

class GetOrderByIdParams(BaseModel):
    order_id: str = Field(..., description="The unique identifier for the order.")

class GetCustomerOrdersParams(BaseModel):
    customer_id: str = Field(..., description="The customer's unique identifier.")

class CancelOrderParams(BaseModel):
    order_id: str = Field(..., description="The order_id to cancel.")

# Mapping from function name to its corresponding Pydantic model
params_model_map = {
    "get_user": GetUserParams,
    "get_order_by_id": GetOrderByIdParams,
    "get_customer_orders": GetCustomerOrdersParams,
    "cancel_order": CancelOrderParams
}

################################################################################
# 2) Fake Database and Tool-Dispatch
################################################################################

class FakeDatabase:
    def __init__(self):
        self.customers = [
            {"id": "1213210", "name": "John Doe", "email": "john@gmail.com", "phone": "123-456-7890", "username": "johndoe"},
            {"id": "2837622", "name": "Priya Patel", "email": "priya@candy.com", "phone": "987-654-3210", "username": "priya123"},
            {"id": "3924156", "name": "Liam Nguyen", "email": "lnguyen@yahoo.com", "phone": "555-123-4567", "username": "liamn"},
            {"id": "4782901", "name": "Aaliyah Davis", "email": "aaliyahd@hotmail.com", "phone": "111-222-3333", "username": "adavis"},
            {"id": "5190753", "name": "Hiroshi Nakamura", "email": "hiroshi@gmail.com", "phone": "444-555-6666", "username": "hiroshin"},
            {"id": "6824095", "name": "Fatima Ahmed", "email": "fatimaa@outlook.com", "phone": "777-888-9999", "username": "fatimaahmed"},
            {"id": "7135680", "name": "Alejandro Rodriguez", "email": "arodriguez@protonmail.com", "phone": "222-333-4444", "username": "alexr"},
            {"id": "8259147", "name": "Megan Anderson", "email": "megana@gmail.com", "phone": "666-777-8888", "username": "manderson"},
            {"id": "9603481", "name": "Kwame Osei", "email": "kwameo@yahoo.com", "phone": "999-000-1111", "username": "kwameo"},
            {"id": "1057426", "name": "Mei Lin", "email": "meilin@gmail.com", "phone": "333-444-5555", "username": "mlin"}
        ]
        self.orders = [
            {"id": "24601", "customer_id": "1213210", "product": "Wireless Headphones", "quantity": 1, "price": 79.99, "status": "Shipped"},
            {"id": "13579", "customer_id": "1213210", "product": "Smartphone Case", "quantity": 2, "price": 19.99, "status": "Processing"},
            {"id": "97531", "customer_id": "2837622", "product": "Bluetooth Speaker", "quantity": 1, "price": "49.99", "status": "Shipped"},
            {"id": "86420", "customer_id": "3924156", "product": "Fitness Tracker", "quantity": 1, "price": 129.99, "status": "Delivered"},
            {"id": "54321", "customer_id": "4782901", "product": "Laptop Sleeve", "quantity": 3, "price": 24.99, "status": "Shipped"},
            {"id": "19283", "customer_id": "5190753", "product": "Wireless Mouse", "quantity": 1, "price": 34.99, "status": "Processing"},
            {"id": "74651", "customer_id": "6824095", "product": "Gaming Keyboard", "quantity": 1, "price": 89.99, "status": "Delivered"},
            {"id": "30298", "customer_id": "7135680", "product": "Portable Charger", "quantity": 2, "price": 29.99, "status": "Shipped"},
            {"id": "47652", "customer_id": "8259147", "product": "Smartwatch", "quantity": 1, "price": 199.99, "status": "Processing"},
            {"id": "61984", "customer_id": "9603481", "product": "Noise-Cancelling Headphones", "quantity": 1, "price": 149.99, "status": "Shipped"},
            {"id": "58243", "customer_id": "1057426", "product": "Wireless Earbuds", "quantity": 2, "price": 99.99, "status": "Delivered"},
            {"id": "90357", "customer_id": "1213210", "product": "Smartphone Case", "quantity": 1, "price": 19.99, "status": "Shipped"},
            {"id": "28164", "customer_id": "2837622", "product": "Wireless Headphones", "quantity": 2, "price": 79.99, "status": "Processing"}
        ]
    
    def get_user(self, key, value):
        if key in {"email", "phone", "username"}:
            for customer in self.customers:
                if customer[key] == value:
                    return customer
            return f"Couldn't find a user with {key} of {value}"
        else:
            raise ValueError(f"Invalid key: {key}")
    
    def get_order_by_id(self, order_id):
        for order in self.orders:
            if order["id"] == order_id:
                return order
        return None
    
    def get_customer_orders(self, customer_id):
        return [order for order in self.orders if order["customer_id"] == customer_id]
    
    def cancel_order(self, order_id):
        order = self.get_order_by_id(order_id)
        if order:
            if order["status"] == "Processing":
                order["status"] = "Cancelled"
                return "Cancelled the order"
            else:
                return "Order has already shipped. Can't cancel it."
        return "Can't find that order!"

db = FakeDatabase()

def process_tool_call(tool_name, tool_input):
    if tool_name == "get_user":
        return db.get_user(tool_input["key"], tool_input["value"])
    elif tool_name == "get_order_by_id":
        return db.get_order_by_id(tool_input["order_id"])
    elif tool_name == "get_customer_orders":
        return db.get_customer_orders(tool_input["customer_id"])
    elif tool_name == "cancel_order":
        return db.cancel_order(tool_input["order_id"])
    else:
        return "Unknown tool!"

################################################################################
# 3) Define OpenAI Tools Using Pydantic
################################################################################

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_user",
            "description": "Looks up a user by email, phone, or username.",
            "parameters": GetUserParams.model_json_schema()
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_order_by_id",
            "description": "Retrieves details of a specific order (id, product, quantity, price, status).",
            "parameters": GetOrderByIdParams.model_json_schema()
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer_orders",
            "description": "Retrieves a list of orders belonging to a user based on the customer's id.",
            "parameters": GetCustomerOrdersParams.model_json_schema()
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_order",
            "description": "Cancels an order if it is 'Processing'.",
            "parameters": CancelOrderParams.model_json_schema()
        }
    }
]

################################################################################
# 4) A Simple Chat Loop with Function Calling Using the Latest API
################################################################################

def simple_chat():
    """
    Continuously prompt the user for input, send the conversation to the
    OpenAI ChatCompletion endpoint with tool definitions, and handle
    tool calls or direct responses.
    """
    messages = []
    system_message = {
        "role": "system",
        "content": "You are a TechNova Customer Support agent. Be helpful, professional, and concise."
    }
    messages.append(system_message)
    
    print("\nTechNova Customer Support: Welcome to the TechNova Customer Support")

    while True:
        user_input = input("\nUser: ")
        if not user_input.strip():
            print("Goodbye!")
            break

        messages.append({"role": "user", "content": user_input})

        while True:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
            
            assistant_message = response.choices[0].message
            
            # Check if the assistant wants to call a tool
            if assistant_message.tool_calls:
                # Save the assistant's message with the tool call
                messages.append(assistant_message)
                
                # Process each tool call
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    try:
                        function_args = json.loads(tool_call.function.arguments)
                    except Exception as e:
                        print(f"Error parsing tool arguments: {e}")
                        break

                    print(f"\n[Assistant is calling the tool: {function_name} with args={function_args}]")

                    try:
                        # Validate parameters
                        if function_name in params_model_map:
                            params = params_model_map[function_name](**function_args)
                            tool_result = process_tool_call(function_name, function_args)
                        else:
                            tool_result = f"Unknown tool: {function_name}"
                    except Exception as e:
                        print(f"Error validating tool arguments: {e}")
                        tool_result = f"Error: {str(e)}"

                    # Append the tool response
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": json.dumps(tool_result)
                    })
                
                # Get the final response after tool use
                continue
            else:
                # No tool call, just a regular message
                print("\nTechNova Support:", assistant_message.content)
                messages.append({"role": "assistant", "content": assistant_message.content})
                break

if __name__ == "__main__":
    simple_chat()
