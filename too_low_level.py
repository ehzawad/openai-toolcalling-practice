import os
import requests
import json

# Get API key from environment variable
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print("Error: OPENAI_API_KEY environment variable is not set")
    exit(1)

# API endpoint
url = "https://api.openai.com/v1/chat/completions"

# Headers
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# Simple calculator function
def calculator(operation, x, y):
    if operation == "add":
        return x + y
    elif operation == "subtract":
        return x - y
    elif operation == "multiply":
        return x * y
    elif operation == "divide":
        if y == 0:
            return "Error: Division by zero"
        return x / y
    else:
        return f"Error: Unknown operation '{operation}'"

# Define calculator tool
calculator_tool = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "A simple calculator that can add, subtract, multiply, and divide two numbers",
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                    "description": "The mathematical operation to perform"
                },
                "x": {
                    "type": "number",
                    "description": "The first number"
                },
                "y": {
                    "type": "number",
                    "description": "The second number"
                }
            },
            "required": ["operation", "x", "y"]
        }
    }
}

def make_openai_request(prompt, use_tools=False):
    # Basic payload
    payload = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": prompt}]
    }
    
    # Add tools if specified
    if use_tools:
        payload["tools"] = [calculator_tool]
        payload["tool_choice"] = "auto"
    
    try:
        print(f"Sending request with prompt: '{prompt}'")
        response = requests.post(url, headers=headers, json=payload)
        
        # Check if request was successful
        response.raise_for_status()
        
        # Parse the response JSON
        result = response.json()
        
        # Extract the message
        message = result["choices"][0]["message"]
        
        # Check if the model used a tool
        if "tool_calls" in message and message["tool_calls"]:
            print("\nModel used tool(s):")
            for tool_call in message["tool_calls"]:
                function_name = tool_call["function"]["name"]
                function_args = json.loads(tool_call["function"]["arguments"])
                
                print(f"Tool call: {function_name}")
                print(f"Arguments: {function_args}")
                
                # Handle calculator function
                if function_name == "calculator":
                    operation = function_args.get("operation")
                    x = function_args.get("x")
                    y = function_args.get("y")
                    
                    result = calculator(operation, x, y)
                    print(f"Calculator result: {result}")
        
        # Print the content of the message
        if message.get("content"):
            print("\nModel response:")
            print(message["content"])
        
        return message
        
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None

def main():
    # Example 1: Direct question (no tools)
    print("\n=== Example 1: Direct Question (No Tools) ===")
    make_openai_request("What is 245 + 367?")
    
    # Example 2: With calculator tool
    print("\n=== Example 2: Using Calculator Tool ===")
    make_openai_request("Calculate 245 + 367 for me", use_tools=True)
    
    # Example 3: Complex calculation
    print("\n=== Example 3: Complex Calculation ===")
    make_openai_request("If I have 150 and divide by 3, then multiply by 7, what do I get?", use_tools=True)

if __name__ == "__main__":
    main()
