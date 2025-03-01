import os
import re
import json
import inspect
from openai import OpenAI

# Initialize the client
client = OpenAI()

def execute_python_code(code):
    """Execute Python code in a controlled environment and return the output"""
    # Create a dictionary to capture local variables created during execution
    local_vars = {}
    
    # Capture stdout in a string
    import io
    import sys
    from contextlib import redirect_stdout
    
    # Buffer for output
    output_buffer = io.StringIO()
    
    # Execute the code with output redirection
    try:
        with redirect_stdout(output_buffer):
            # Using exec to execute the code
            exec(code, {"__builtins__": __builtins__}, local_vars)
        
        # Get the output
        output = output_buffer.getvalue()
        
        return {
            "success": True,
            "output": output,
            "variables": {k: v for k, v in local_vars.items() if not k.startswith('_')}
        }
    except Exception as e:
        # Return error information if execution fails
        return {
            "success": False,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "line_number": getattr(e, 'lineno', None)
        }

def extract_code_blocks(text):
    """Extract Python code blocks from markdown-formatted text"""
    # Pattern to match code blocks
    pattern = r"```(?:python)?\n(.*?)\n```"
    # Find all code blocks
    code_blocks = re.findall(pattern, text, re.DOTALL)
    return code_blocks

def chat_with_code_execution(prompt):
    """Chat with GPT-4o and execute any Python code it generates"""
    
    # Initial system message instructing the model to solve with code
    messages = [
        {
            "role": "system",
            "content": (
                "You are a computational assistant that solves problems using Python code. "
                "For any mathematical calculation, write executable Python code to solve it. "
                "Present your code in ```python code blocks. "
                "After providing code, you will receive the execution results. "
                "Explain both your approach and the final answer clearly."
            )
        },
        {"role": "user", "content": prompt}
    ]
    
    # First, get the model's initial response with code
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.3,  # Lower temperature for more deterministic results
    )
    
    # Get the assistant's message
    assistant_message = response.choices[0].message
    
    # Extract the code blocks from the response
    code_blocks = extract_code_blocks(assistant_message.content)
    
    # If no code blocks found
    if not code_blocks:
        print("The assistant did not provide any executable code blocks.")
        return {
            "answer": assistant_message.content,
            "code": None,
            "execution_result": None
        }
    
    # Execute each code block and save results
    execution_results = []
    for i, code in enumerate(code_blocks):
        print(f"\nExecuting code block {i+1}:")
        print("```python")
        print(code)
        print("```")
        
        # Execute the code
        result = execute_python_code(code)
        execution_results.append(result)
        
        if result["success"]:
            print("\nExecution output:")
            print(result["output"])
            
            # If there are variables to display
            if result["variables"]:
                print("\nVariables after execution:")
                for var_name, var_value in result["variables"].items():
                    print(f"{var_name} = {var_value}")
        else:
            print(f"\nExecution failed: {result['error_type']}: {result['error_message']}")
    
    # Add the execution results to messages and get final answer
    messages.append(assistant_message)
    messages.append({
        "role": "user",
        "content": f"Here are the results of executing your code: {json.dumps(execution_results, default=str)}. Based on these results, what's the final answer to my question?"
    })
    
    # Get final response
    final_response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.3,
    )
    
    final_answer = final_response.choices[0].message.content
    
    return {
        "answer": final_answer,
        "code": code_blocks,
        "execution_result": execution_results
    }

def main():
    examples = [
        "What is 245 + 367?",
        "If I have 150 and divide by 3, then multiply by 7, what do I get?",
        "Calculate the compound interest on a principal of $10,000 with an annual interest rate of 5% compounded monthly for 3 years."
    ]
    
    for i, example in enumerate(examples):
        print(f"\n=== Example {i+1}: {example} ===")
        
        result = chat_with_code_execution(example)
        
        print("\n🤖 FINAL ANSWER:")
        print("-" * 80)
        print(result["answer"])
        print("-" * 80)

if __name__ == "__main__":
    main()
