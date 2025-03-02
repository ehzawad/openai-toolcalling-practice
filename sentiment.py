import os
import json
import wikipedia
from dotenv import load_dotenv
from openai import OpenAI

# Load your OpenAI API key from an .env file or environment variable
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TARGET_LANG = "bn"  # Default target language for translation
# ------------------------------------------------------------------
# Define OpenAI tools
# ------------------------------------------------------------------

sentiment_tools = [
    {
        "type": "function",
        "function": {
            "name": "print_sentiment_scores",
            "description": "Prints the sentiment scores of a given text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "positive_score": {
                        "type": "number",
                        "description": "The positive sentiment score, ranging from 0.0 to 1.0."
                    },
                    "negative_score": {
                        "type": "number",
                        "description": "The negative sentiment score, ranging from 0.0 to 1.0."
                    },
                    "neutral_score": {
                        "type": "number",
                        "description": "The neutral sentiment score, ranging from 0.0 to 1.0."
                    }
                },
                "required": ["positive_score", "negative_score", "neutral_score"]
            }
        }
    }
]

entities_tools = [
    {
        "type": "function",
        "function": {
            "name": "print_entities",
            "description": "Prints extracted named entities.",
            "parameters": {
                "type": "object",
                "properties": {
                    "entities": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "The extracted entity name."
                                },
                                "type": {
                                    "type": "string",
                                    "description": "The entity type (e.g., PERSON, ORGANIZATION, LOCATION)."
                                },
                                "context": {
                                    "type": "string",
                                    "description": "The context in which the entity appears in the text."
                                }
                            },
                            "required": ["name", "type", "context"]
                        }
                    }
                },
                "required": ["entities"]
            }
        }
    }
]

classification_tools = [
    {
        "type": "function",
        "function": {
            "name": "print_article_classification",
            "description": "Prints the classification results.",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "description": "The overall subject of the article."
                    },
                    "summary": {
                        "type": "string",
                        "description": "A paragraph summary of the article."
                    },
                    "keywords": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "description": "List of keywords and topics in the article."
                        }
                    },
                    "categories": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "The category name."
                                },
                                "score": {
                                    "type": "number",
                                    "description": "The classification score for the category, ranging from 0.0 to 1.0."
                                }
                            },
                            "required": ["name", "score"]
                        }
                    }
                },
                "required": ["subject", "summary", "keywords", "categories"]
            }
        }
    }
]

translation_tools = [
    {
        "type": "function",
        "function": {
            "name": "translate_text",
            "description": "Translates the given text into a target language.",
            "parameters": {
                "type": "object",
                "properties": {
                    "translated_text": {
                        "type": "string",
                        "description": "The translated text."
                    }
                },
                "required": ["translated_text"]
            }
        }
    }
]

# ------------------------------------------------------------------
# Helper: Extract function call result from the API response
# ------------------------------------------------------------------

def extract_function_result(response, function_name):
    """
    Extracts and parses the function call result from the response for the given function name.
    """
    message = response.choices[0].message
    
    if message.tool_calls:
        for tool_call in message.tool_calls:
            if tool_call.function.name == function_name:
                try:
                    return json.loads(tool_call.function.arguments)
                except Exception as e:
                    print("Error parsing function result:", e)
    return None

# ------------------------------------------------------------------
# Sentiment Analysis Functions using GPT-4o
# ------------------------------------------------------------------

def analyze_sentiment(content):
    """
    Analyzes the sentiment of the given text using OpenAI's GPT-4 function calling.
    """
    query = f"""
    <text>
    {content}
    </text>

    Only use the print_sentiment_scores function.
    """
    messages = [{"role": "user", "content": query}]
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=sentiment_tools,
        tool_choice={"type": "function", "function": {"name": "print_sentiment_scores"}},
        max_tokens=4096
    )
    result = extract_function_result(response, "print_sentiment_scores")
    if result:
        print("Sentiment Analysis (JSON):")
        print(json.dumps(result, indent=2))
    else:
        print("No sentiment analysis found in the response.")

# ------------------------------------------------------------------
# Entity Extraction Function using GPT-4
# ------------------------------------------------------------------

def extract_entities(text):
    """
    Extracts named entities from the given text using OpenAI's GPT-4 function calling.
    """
    query = f"""
    <document>
    {text}
    </document>

    Use the print_entities function.
    """
    messages = [{"role": "user", "content": query}]
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=entities_tools,
        tool_choice={"type": "function", "function": {"name": "print_entities"}},
        max_tokens=4096
    )
    result = extract_function_result(response, "print_entities")
    if result:
        print("Extracted Entities (JSON):")
        print(json.dumps(result, indent=2))
    else:
        print("No entities found in the response.")

# ------------------------------------------------------------------
# Article Classification Function using Wikipedia content and GPT-4
# ------------------------------------------------------------------

def generate_json_for_article(subject):
    """
    Retrieves a Wikipedia article for the subject and classifies its content using GPT-4 function calling.
    """
    try:
        page = wikipedia.page(subject, auto_suggest=True)
    except Exception as e:
        print(f"Error retrieving Wikipedia page for {subject}: {e}")
        return

    query = f"""
    <document>
    {page.content}
    </document>

    Use the print_article_classification function. Example categories are Politics, Sports, Technology, Entertainment, Business.
    """
    messages = [{"role": "user", "content": query}]
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=classification_tools,
        tool_choice={"type": "function", "function": {"name": "print_article_classification"}},
        max_tokens=4096
    )
    result = extract_function_result(response, "print_article_classification")
    if result:
        print("Text Classification (JSON):")
        print(json.dumps(result, indent=2))
    else:
        print("No text classification found in the response.")

# ------------------------------------------------------------------
# Translation Function using GPT-4o
# ------------------------------------------------------------------

def translate(text, target_language=TARGET_LANG):
    """
    Translates the given text to the target language using GPT-4 function calling.
    Default target language is Spanish.
    """
    query = f"Translate the following text to {target_language}: \"{text}\". Return only the translated text in the translate_text function."
    messages = [{"role": "user", "content": query}]
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=translation_tools,
        tool_choice={"type": "function", "function": {"name": "translate_text"}},
        max_tokens=4096
    )
    result = extract_function_result(response, "translate_text")
    if result:
        print("Translation (JSON):")
        print(json.dumps(result, indent=2))
    else:
        print("No translation found in the response.")

# Example usage
if __name__ == "__main__":
    # Example sentiment analysis calls:
    tweet_negative = "I'm a HUGE hater of pickles. I actually despise pickles. They are garbage."
    tweet_positive = "OMG I absolutely love taking bubble baths soooo much!!!!"
    tweet_neutral  = "Honestly I have no opinion on taking baths"

    print("Analyzing negative sentiment tweet:")
    analyze_sentiment(tweet_negative)
    print("\nAnalyzing positive sentiment tweet:")
    analyze_sentiment(tweet_positive)
    print("\nAnalyzing neutral sentiment tweet:")
    analyze_sentiment(tweet_neutral)

    # Example entity extraction:
    sample_text = "John works at Google in New York. He met with Sarah, the CEO of Acme Inc., last week in San Francisco."
    print("\nExtracting entities:")
    extract_entities(sample_text)

    # Example article classification calls:
    print("\nClassifying article for 'Jeff Goldblum':")
    generate_json_for_article("Jeff Goldblum")
    print("\nClassifying article for 'Octopus':")
    generate_json_for_article("Octopus")
    print("\nClassifying article for 'Herbert Hoover':")
    generate_json_for_article("Herbert Hoover")

    # Example translation call:
    print("\nTranslating text:")
    translate("how much does this cost")
