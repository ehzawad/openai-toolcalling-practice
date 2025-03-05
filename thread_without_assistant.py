import os
import time
import json
from openai import OpenAI
from typing import Dict, List, Any, Optional, Union

class ThreadSessionManager:
    """
    A class to manage OpenAI Thread sessions with assistants.
    This class provides methods to create, retrieve, and manage conversations.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the ThreadSessionManager.
        
        Args:
            api_key: OpenAI API key (optional, will use OPENAI_API_KEY env var if not provided)
        """
        self.client = OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))
        
    def create_thread(self) -> str:
        """
        Create a new thread.
        
        Returns:
            str: The ID of the created thread
        """
        thread = self.client.beta.threads.create()
        return thread.id
    
    def retrieve_thread(self, thread_id: str) -> Dict:
        """
        Retrieve details about a specific thread.
        
        Args:
            thread_id: The ID of the thread to retrieve
            
        Returns:
            Dict: The thread object
        """
        thread = self.client.beta.threads.retrieve(thread_id)
        return {
            "id": thread.id,
            "created_at": thread.created_at,
            "metadata": thread.metadata
        }
    
    def add_message(self, thread_id: str, content: str, files: List[str] = None) -> str:
        """
        Add a message to a thread.
        
        Args:
            thread_id: The ID of the thread to add the message to
            content: The content of the message
            files: Optional list of file IDs to attach
            
        Returns:
            str: The ID of the created message
        """
        # Create message with or without attachments
        if files:
            # If files are provided, we need to use the attachments parameter
            attachments = [{"file_id": file_id, "type": "file_attachment"} for file_id in files]
            message = self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=content,
                attachments=attachments
            )
        else:
            # Without files, just create a simple message
            message = self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=content
            )
        return message.id
    
    def list_messages(self, thread_id: str, limit: int = 20) -> List[Dict]:
        """
        List messages in a thread.
        
        Args:
            thread_id: The ID of the thread to list messages from
            limit: Maximum number of messages to return
            
        Returns:
            List[Dict]: List of message objects
        """
        messages = self.client.beta.threads.messages.list(
            thread_id=thread_id,
            limit=limit
        )
        
        result = []
        for msg in messages.data:
            content_parts = []
            for content_item in msg.content:
                if content_item.type == 'text':
                    content_parts.append({
                        "type": "text",
                        "text": content_item.text.value
                    })
                # Add more content type handling as needed (images, files, etc.)
            
            result.append({
                "id": msg.id,
                "role": msg.role,
                "created_at": msg.created_at,
                "content": content_parts
            })
            
        return result
    
    def run_assistant(self, thread_id: str, assistant_id: str, 
                     instructions: Optional[str] = None, 
                     wait_for_completion: bool = True,
                     poll_interval: float = 1.0,
                     timeout: float = 120.0) -> Dict:
        """
        Run an assistant on a thread.
        
        Args:
            thread_id: The ID of the thread
            assistant_id: The ID of the assistant to run
            instructions: Optional override instructions for this run
            wait_for_completion: Whether to wait for the run to complete
            poll_interval: How often to check run status (in seconds)
            timeout: Maximum time to wait for completion (in seconds)
            
        Returns:
            Dict: The run object or its final state if waited for completion
        """
        run_params = {
            "thread_id": thread_id,
            "assistant_id": assistant_id
        }
        
        if instructions:
            run_params["instructions"] = instructions
            
        run = self.client.beta.threads.runs.create(**run_params)
        
        if not wait_for_completion:
            return {
                "id": run.id,
                "status": run.status,
                "created_at": run.created_at
            }
        
        # Wait for completion
        start_time = time.time()
        while run.status in ["queued", "in_progress"]:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Run timed out after {timeout} seconds")
            
            time.sleep(poll_interval)
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
        
        result = {
            "id": run.id,
            "status": run.status,
            "created_at": run.created_at,
            "completed_at": run.completed_at
        }
        
        # If there was an error, include it
        if run.status == "failed" and hasattr(run, "last_error"):
            result["error"] = {
                "code": run.last_error.code,
                "message": run.last_error.message
            }
            
        return result

    def get_run_steps(self, thread_id: str, run_id: str) -> List[Dict]:
        """
        Get the steps of a run.
        
        Args:
            thread_id: The ID of the thread
            run_id: The ID of the run
            
        Returns:
            List[Dict]: List of run step objects
        """
        steps = self.client.beta.threads.runs.steps.list(
            thread_id=thread_id,
            run_id=run_id
        )
        
        result = []
        for step in steps.data:
            step_info = {
                "id": step.id,
                "type": step.type,
                "status": step.status,
                "created_at": step.created_at,
                "completed_at": step.completed_at
            }
            
            # Add step details based on type
            if step.type == "message_creation":
                step_info["message_id"] = step.step_details.message_creation.message_id
            elif step.type == "tool_calls":
                tool_calls = []
                for tool_call in step.step_details.tool_calls:
                    if tool_call.type == "function":
                        tool_calls.append({
                            "type": "function",
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments
                            }
                        })
                step_info["tool_calls"] = tool_calls
                
            result.append(step_info)
            
        return result
        
    def cancel_run(self, thread_id: str, run_id: str) -> Dict:
        """
        Cancel a run.
        
        Args:
            thread_id: The ID of the thread
            run_id: The ID of the run to cancel
            
        Returns:
            Dict: The updated run object
        """
        run = self.client.beta.threads.runs.cancel(
            thread_id=thread_id,
            run_id=run_id
        )
        
        return {
            "id": run.id,
            "status": run.status,
            "created_at": run.created_at,
            "cancelled_at": run.cancelled_at
        }
    
    def submit_tool_outputs(self, thread_id: str, run_id: str, 
                           tool_outputs: List[Dict[str, str]]) -> Dict:
        """
        Submit outputs for tool calls.
        
        Args:
            thread_id: The ID of the thread
            run_id: The ID of the run
            tool_outputs: List of tool outputs, each with tool_call_id and output
            
        Returns:
            Dict: The updated run object
        """
        run = self.client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread_id,
            run_id=run_id,
            tool_outputs=tool_outputs
        )
        
        return {
            "id": run.id,
            "status": run.status,
            "created_at": run.created_at
        }
    
    def delete_thread(self, thread_id: str) -> bool:
        """
        Delete a thread.
        
        Args:
            thread_id: The ID of the thread to delete
            
        Returns:
            bool: True if deletion was successful
        """
        response = self.client.beta.threads.delete(thread_id)
        return response.deleted


# Example usage
if __name__ == "__main__":
    # Set your OpenAI API key here or as an environment variable
    API_KEY = os.environ.get("OPENAI_API_KEY")
    
    # Initialize the manager
    manager = ThreadSessionManager(api_key=API_KEY)
    
    # Create a new thread
    print("Creating a new thread...")
    thread_id = manager.create_thread()
    print(f"Thread created with ID: {thread_id}")
    
    # Add a message to the thread
    print("\nAdding a message to the thread...")
    message_content = "This is my first message in this thread"
    message_id = manager.add_message(thread_id, message_content)
    print(f"Message added with ID: {message_id}")
    
    # Add another message to the thread
    print("\nAdding a second message to the thread...")
    message_content = "And this is my second message in the same thread"
    message_id = manager.add_message(thread_id, message_content)
    print(f"Second message added with ID: {message_id}")
    
    # List messages in the thread
    print("\nListing messages in the thread:")
    messages = manager.list_messages(thread_id)
    for msg in messages:
        role = msg["role"]
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(msg["created_at"]))
        content_text = ""
        for content in msg["content"]:
            if content["type"] == "text":
                content_text += content["text"]
        
        print(f"[{timestamp}] {role.upper()}: {content_text}")
    
    # Retrieve thread details
    print("\nRetrieving thread details:")
    thread_details = manager.retrieve_thread(thread_id)
    print(f"Thread ID: {thread_details['id']}")
    print(f"Created at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(thread_details['created_at']))}")
    
    # In a real application, you might want to keep the thread for future interactions
    # For this example, we'll delete it
    print("\nDeleting the thread...")
    deletion_result = manager.delete_thread(thread_id)
    print(f"Thread deletion {'successful' if deletion_result else 'failed'}")
    
    
    print("\n-----------------------------------------")
    print("NOTE: If you want to use Assistants with threads, you need to:")
    print("1. Create an Assistant in the OpenAI platform or via API")
    print("2. Get the Assistant ID (starts with 'asst_')")
    print("3. Use the run_assistant method with your actual Assistant ID")
    print("-----------------------------------------")
    print("Example code for running an Assistant (once you have an Assistant ID):")
    print("""
    # Run an assistant on a thread
    run_result = manager.run_assistant(
        thread_id=thread_id,
        assistant_id="asst_your_actual_assistant_id",
        wait_for_completion=True
    )
    print(f"Run completed with status: {run_result['status']}")
    
    # Get run steps
    steps = manager.get_run_steps(thread_id, run_result["id"])
    for step in steps:
        print(f"Step type: {step['type']}, Status: {step['status']}")
    """)
