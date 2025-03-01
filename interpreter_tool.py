import os
import time
from openai import OpenAI

# Initialize the client
client = OpenAI()

def create_assistant_with_code_interpreter():
    """Create an assistant with code interpreter capabilities"""
    assistant = client.beta.assistants.create(
        name="Math Assistant",
        instructions="You are a mathematical assistant that solves calculations with precision. Use code execution to ensure all calculations are correct. Show your work by writing Python code and explaining the process.",
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
    
    # Wait for the run to complete
    while True:
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
        if run_status.status == "completed":
            break
        elif run_status.status in ["failed", "cancelled", "expired"]:
            print(f"Run ended with status: {run_status.status}")
            return None
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

def display_message(message):
    """Display the assistant's message with any code outputs"""
    if not message:
        print("No response received.")
        return
    
    print("\nAssistant's Response:")
    for content_part in message.content:
        if content_part.type == "text":
            print(content_part.text.value)
        elif content_part.type == "image":
            print("[Image was generated]")

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
        display_message(message)
        
        # Example 2: More complex calculation
        print("\n=== Example 2: Complex Calculation ===")
        message = add_message_and_run(
            thread.id,
            assistant.id,
            "If I have 150 and divide by 3, then multiply by 7, what do I get?"
        )
        display_message(message)
        
        # Example 3: Even more complex mathematical operation
        print("\n=== Example 3: Advanced Calculation ===")
        message = add_message_and_run(
            thread.id,
            assistant.id,
            "Calculate the compound interest on a principal of $10,000 with an annual interest rate of 5% compounded monthly for 3 years."
        )
        display_message(message)
        
    finally:
        # Clean up: delete the assistant
        client.beta.assistants.delete(assistant.id)
        print(f"\nDeleted assistant with ID: {assistant.id}")

if __name__ == "__main__":
    main()
