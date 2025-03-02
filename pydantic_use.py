import os
import json
from enum import Enum
from openai import OpenAI
from pydantic import BaseModel, Field

# Define an Enum for valid operations
class OperationEnum(str, Enum):
    add = "add"
    subtract = "subtract"
    multiply = "multiply"
    divide = "divide"

# Pydantic model for the calculator function parameters
class CalculatorParams(BaseModel):
    operation: OperationEnum = Field(..., description="The mathematical operation to perform")
    x: float = Field(..., description="The first number")
    y: float = Field(..., description="The second number")

# Initialize the OpenAI client (assumes OPENAI_API_KEY is set)
client = OpenAI()

# Calculator function performing basic arithmetic operations
def calculator(operation, x, y):
    if operation == OperationEnum.add:
        return x + y
    elif operation == OperationEnum.subtract:
        return x - y
    elif operation == OperationEnum.multiply:
        return x * y
    elif operation == OperationEnum.divide:
        if y == 0:
            return "Error: Division by zero"
        return x / y
    else:
        return f"Error: Unknown operation '{operation}'"

def make_openai_request(prompt, use_tools=False):
    # Generate JSON Schema from the CalculatorParams model
    schema = CalculatorParams.model_json_schema()

    # Define available tools using the generated JSON Schema
    tools = [
        {
            "type": "function",
            "function": {
                "name": "calculator",
                "description": "A simple calculator that can add, subtract, multiply, and divide two numbers",
                "parameters": {
                    "type": "object",
                    "properties": schema["properties"],
                    "required": schema.get("required", list(schema["properties"].keys()))
                }
            }
        }
    ]
    
    # Initial conversation message
    messages = [{"role": "user", "content": prompt}]
    
    # Conversation loop
    while True:
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
        message = response.choices[0].message
        
        # Add the assistant message to conversation history
        messages.append({
            "role": "assistant",
            "content": message.content,
            "tool_calls": message.tool_calls if hasattr(message, "tool_calls") else None
        })
        
        # Process any tool calls from the model
        if message.tool_calls:
            print("\nModel used tool(s):")
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                function_args = tool_call.function.arguments
                
                # Parse and validate the arguments using CalculatorParams
                try:
                    params = CalculatorParams.model_validate_json(function_args)
                except Exception as e:
                    print(f"Error parsing arguments: {e}")
                    continue
                
                print(f"Tool call: {function_name}")
                print(f"Arguments: {params.model_dump()}")
                
                # Execute the calculator function based on the parsed parameters
                if function_name == "calculator":
                    result = calculator(params.operation, params.x, params.y)
                    print(f"Calculator result: {result}")
                    
                    # Append the tool response back into the conversation
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": str(result)
                    })
            
            # Continue the conversation with the updated messages
            continue
        
        # Exit loop when there are no more tool calls
        break
    
    # Output the final model response
    if message.content:
        print("\nFinal model response:")
        print(message.content)
    
    return message

def main():
    # Example 1: Direct question without using tools
    print("\n=== Example 1: Direct Question (No Tools) ===")
    make_openai_request("What is 245 + 367?")
    
    # Example 2: Using the calculator tool
    print("\n=== Example 2: Using Calculator Tool ===")
    make_openai_request("Calculate 245 + 367 for me", use_tools=True)
    
    # Example 3: A more complex calculation
    print("\n=== Example 3: Complex Calculation ===")
    make_openai_request("If I have 150 and divide by 3, then multiply by 7, what do I get?", use_tools=True)

if __name__ == "__main__":
    main()

