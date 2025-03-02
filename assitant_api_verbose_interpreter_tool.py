import os
import time
import json
from openai import OpenAI

# Initialize the client
client = OpenAI()

def create_assistant_with_code_interpreter():
    """Create an assistant with code interpreter capabilities"""
    assistant = client.beta.assistants.create(
        name="Math Assistant",
        instructions="""You are a mathematical assistant that solves calculations with precision. 
        Always use the code interpreter to perform calculations.
        Show your work by writing detailed Python code.
        For any calculation, no matter how simple, write and execute Python code.
        Explain your approach before and after showing code.""",
        model="gpt-4o",
        tools=[{"type": "code_interpreter"}]
    )
    return assistant

def create_thread():
    """Create a new thread for conversation"""
    thread = client.beta.threads.create()
    return thread

def add_message_and_run(thread_id, assistant_id, content):
    """Add a user message to the thread and run the assistant"""
    # Add the user's message to the thread
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=content
    )
    
    # Run the assistant on the thread
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    
    print("Processing request...")
    
    # Wait for the run to complete
    while True:
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
        
        # Print the current run status
        print(f"Status: {run_status.status}", end="\r")
        
        if run_status.status == "completed":
            print(f"Status: {run_status.status} ✓")
            break
        elif run_status.status in ["failed", "cancelled", "expired"]:
            print(f"Run ended with status: {run_status.status}")
            return None
            
        # Check for tool use
        if run_status.status == "requires_action":
            # This would handle any required actions, though code interpreter
            # typically doesn't require this
            print(f"Status: {run_status.status} - Tool execution in progress")
            
        time.sleep(1)
    
    # Get the assistant's messages after the run
    messages = client.beta.threads.messages.list(
        thread_id=thread_id
    )
    
    # Return the most recent message from the assistant
    for message in messages.data:
        if message.role == "assistant":
            return message
    
    return None

def display_message_with_code_details(message):
    """Display the assistant's message including code blocks and outputs"""
    if not message:
        print("No response received.")
        return
    
    print("\n🤖 ASSISTANT RESPONSE:")
    print("=" * 80)
    
    # Get the run steps to show code execution details
    run_steps = client.beta.threads.runs.steps.list(
        thread_id=message.thread_id,
        run_id=message.run_id
    )
    
    # First show the final response text
    print("\n📝 FINAL ANSWER:")
    print("-" * 80)
    for content_part in message.content:
        if content_part.type == "text":
            print(content_part.text.value)
        elif content_part.type == "image":
            print("[Image was generated]")
    
    # Then show the code execution details from run steps
    print("\n💻 CODE EXECUTION DETAILS:")
    print("-" * 80)
    
    for step in run_steps.data:
        if step.step_details.type == "tool_calls":
            for tool_call in step.step_details.tool_calls:
                if tool_call.type == "code_interpreter":
                    # Show the code that was executed
                    if tool_call.code_interpreter.input:
                        print("\n📌 PYTHON CODE EXECUTED:")
                        print("```python")
                        print(tool_call.code_interpreter.input)
                        print("```")
                    
                    # Show outputs from the code execution
                    if tool_call.code_interpreter.outputs:
                        print("\n📊 CODE EXECUTION OUTPUT:")
                        for output in tool_call.code_interpreter.outputs:
                            if output.type == "logs":
                                print(output.logs)
                            elif output.type == "image":
                                print(f"[Image output generated with MIME type: {output.image.mime_type}]")
    
    print("=" * 80)

def main():
    # Create an assistant with code interpreter
    assistant = create_assistant_with_code_interpreter()
    print(f"Created assistant with ID: {assistant.id}")
    
    # Create a thread
    thread = create_thread()
    print(f"Created thread with ID: {thread.id}")
    
    try:
        # Example 1: Simple calculation
        print("\n=== Example 1: Simple Calculation ===")
        message = add_message_and_run(
            thread.id, 
            assistant.id, 
            "What is 245 + 367?"
        )
        display_message_with_code_details(message)
        
        # Example 2: More complex calculation
        print("\n=== Example 2: Complex Calculation ===")
        message = add_message_and_run(
            thread.id,
            assistant.id,
            "If I have 150 and divide by 3, then multiply by 7, what do I get?"
        )
        display_message_with_code_details(message)
        
        # Example 3: Even more complex mathematical operation
        print("\n=== Example 3: Advanced Calculation ===")
        message = add_message_and_run(
            thread.id,
            assistant.id,
            "Calculate the compound interest on a principal of $10,000 with an annual interest rate of 5% compounded monthly for 3 years."
        )
        display_message_with_code_details(message)
        
    finally:
        # Clean up: delete the assistant
        client.beta.assistants.delete(assistant.id)
        print(f"\nDeleted assistant with ID: {assistant.id}")

if __name__ == "__main__":
    main()
