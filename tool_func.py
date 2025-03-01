import os
from openai import OpenAI

# Initialize the client
client = OpenAI()  # Automatically uses OPENAI_API_KEY environment variable

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

def make_openai_request(prompt, use_tools=False):
    # Define available tools
    tools = [
        {
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
    ]
    
    # Initial messages
    messages = [{"role": "user", "content": prompt}]
    
    # Keep track of the conversation
    while True:
        # API call parameters
        kwargs = {
            "model": "gpt-4o",
            "messages": messages
        }
        
        # Add tools if specified
        if use_tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        
        print(f"Sending request with prompt: '{prompt}'")
        response = client.chat.completions.create(**kwargs)
        
        # Get the response message
        message = response.choices[0].message
        
        # Add assistant's message to conversation history
        messages.append({
            "role": "assistant",
            "content": message.content,
            "tool_calls": message.tool_calls if hasattr(message, "tool_calls") else None
        })
        
        # Check if the model wants to use tools
        if message.tool_calls:
            print("\nModel used tool(s):")
            
            # For each tool call
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                function_args = tool_call.function.arguments
                
                # Parse function arguments
                try:
                    import json
                    arguments = json.loads(function_args)
                except Exception as e:
                    print(f"Error parsing arguments: {e}")
                    continue
                
                print(f"Tool call: {function_name}")
                print(f"Arguments: {arguments}")
                
                # Execute the calculator function
                if function_name == "calculator":
                    operation = arguments.get("operation")
                    x = arguments.get("x")
                    y = arguments.get("y")
                    
                    result = calculator(operation, x, y)
                    print(f"Calculator result: {result}")
                    
                    # Add the tool response to the conversation
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": str(result)
                    })
            
            # Continue the conversation with the tool results
            continue
        
        # If no tool calls, we're done
        break
    
    # Print the final response
    if message.content:
        print("\nFinal model response:")
        print(message.content)
    
    return message

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
