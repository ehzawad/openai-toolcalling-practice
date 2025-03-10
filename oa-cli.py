#!/usr/bin/env python3
import argparse
import json
import os
import sys
import readline
from pathlib import Path
from typing import List, Dict, Any

import tiktoken
from openai import OpenAI

HISTORY_FILE = Path.home() / ".myopenai_history.json"
MODEL = "gpt-4o"  # This model supports 128k context window
MAX_RESPONSE_TOKENS = 4096  # Maximum tokens for the response

def count_tokens(messages: List[Dict[str, Any]]) -> int:
    """Count the number of tokens in a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(MODEL)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")  # Default encoding
    
    num_tokens = 0
    for message in messages:
        # Every message follows <im_start>{role/name}\n{content}<im_end>\n
        num_tokens += 4
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":  # If there's a name, the role is omitted
                num_tokens -= 1  # Role is omitted
    num_tokens += 2  # Every reply is primed with <im_start>assistant
    return num_tokens

def prune_messages_if_needed(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Prune messages if they exceed the model's context window size."""
    # Get accurate token count
    token_count = count_tokens(messages)
    
    # Set context window size for gpt-4o
    max_context_tokens = 128000 - MAX_RESPONSE_TOKENS
    
    # If we're within limits, return the original messages
    if token_count <= max_context_tokens:
        return messages
    
    # Start with all messages and keep removing the oldest until we're under the limit
    pruned_messages = messages.copy()
    
    while token_count > max_context_tokens and len(pruned_messages) > 1:
        # Remove the oldest non-system message
        oldest_non_system_idx = next((i for i, msg in enumerate(pruned_messages) 
                                     if msg["role"] != "system"), 0)
        pruned_messages.pop(oldest_non_system_idx)
        
        # Recalculate token count
        token_count = count_tokens(pruned_messages)
    
    return pruned_messages

def load_history() -> List[Dict[str, Any]]:
    """Load conversation history from file."""
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("Warning: History file corrupted. Starting fresh.")
        return []

def save_history(messages: List[Dict[str, Any]]) -> None:
    """Save conversation history to file."""
    with open(HISTORY_FILE, "w") as f:
        json.dump(messages, f, indent=2)

def get_openai_response(messages: List[Dict[str, Any]], stream: bool = True) -> str:
    """Get response from OpenAI API."""
    client = OpenAI()  # This will read the API key from OPENAI_API_KEY environment variable
    
    try:
        if stream:
            full_response = ""
            response_stream = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                max_tokens=MAX_RESPONSE_TOKENS,
                stream=True,
            )
            
            for chunk in response_stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    full_response += content
            
            print()  # Add a newline at the end
            return full_response
        else:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                max_tokens=MAX_RESPONSE_TOKENS,
            )
            return response.choices[0].message.content
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def interactive_mode(system_message=None, no_stream=False):
    """Run the OpenAI CLI in interactive mode."""
    print("Starting interactive chat with OpenAI gpt-4o model.")
    print("Type 'exit', 'quit', or press Ctrl+D to end the conversation.")
    print("Type 'clear' to clear the conversation history.")
    print()
    
    # Load history
    messages = load_history()
    
    # Add or update system message
    system_msg = system_message or "You are a helpful assistant. Remember the context of our conversation and previous interactions. If asked about previous queries or our conversation history, provide a summary of what we've discussed so far."
    
    # Remove any existing system messages
    messages = [msg for msg in messages if msg["role"] != "system"]
    
    # Add the system message at the beginning
    messages.insert(0, {"role": "system", "content": system_msg})
    
    try:
        while True:
            try:
                # Display prompt and get user input
                user_input = input("\033[1;36m>>> \033[0m")  # Cyan colored prompt
                
                # Handle special commands
                if user_input.lower() in ["exit", "quit"]:
                    break
                elif user_input.lower() == "clear":
                    if HISTORY_FILE.exists():
                        HISTORY_FILE.unlink()
                    print("Conversation history cleared.")
                    messages = [{"role": "system", "content": system_msg}]
                    continue
                elif user_input.strip() == "":
                    continue
                
                # Add user query
                messages.append({"role": "user", "content": user_input})
                
                # Prune messages if needed to fit context window
                messages = prune_messages_if_needed(messages)
                
                # Print a separator before the response
                print("\033[90m" + "-" * 50 + "\033[0m")  # Gray separator
                
                # Get response
                response_text = get_openai_response(messages, not no_stream)
                
                # Add another separator after the response
                print("\033[90m" + "-" * 50 + "\033[0m")  # Gray separator
                
                # Save assistant's response to history
                messages.append({"role": "assistant", "content": response_text})
                save_history(messages)
                
            except KeyboardInterrupt:
                print("\nUse Ctrl+D or type 'exit' to exit.")
                continue
                
    except EOFError:
        print("\nExiting chat. Conversation history saved.")

def main():
    parser = argparse.ArgumentParser(description="OpenAI CLI tool")
    parser.add_argument("query", nargs="?", help="The query to send to OpenAI")
    parser.add_argument("-i", "--interactive", action="store_true", help="Start interactive mode")
    parser.add_argument("--clear", action="store_true", help="Clear conversation history")
    parser.add_argument("--no-stream", action="store_true", help="Disable streaming responses")
    parser.add_argument("--system", help="Set a system message for the conversation")
    
    args = parser.parse_args()
    
    # Check for API key
    if "OPENAI_API_KEY" not in os.environ:
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Please set your OpenAI API key with:")
        print("export OPENAI_API_KEY='your-api-key'")
        sys.exit(1)
    
    if args.clear:
        if HISTORY_FILE.exists():
            HISTORY_FILE.unlink()
        print("Conversation history cleared.")
        return
    
    if args.interactive:
        interactive_mode(args.system, args.no_stream)
        return
    
    if not args.query:
        print("No query provided. Starting interactive mode...")
        interactive_mode(args.system, args.no_stream)
        return
    
    # Load history
    messages = load_history()
    
    # Add or update system message
    system_msg = args.system or "You are a helpful assistant. Remember the context of our conversation and previous interactions. If asked about previous queries or our conversation history, provide a summary of what we've discussed so far."
    
    # Remove any existing system messages
    messages = [msg for msg in messages if msg["role"] != "system"]
    
    # Add the system message at the beginning
    messages.insert(0, {"role": "system", "content": system_msg})
    
    # Add user query
    messages.append({"role": "user", "content": args.query})
    
    # Prune messages if needed to fit context window
    messages = prune_messages_if_needed(messages)
    
    # Get response
    response_text = get_openai_response(messages, not args.no_stream)
    
    # Save assistant's response to history
    messages.append({"role": "assistant", "content": response_text})
    save_history(messages)

if __name__ == "__main__":
    main()
