import os
import json
import boto3
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

import logging
logger = logging.getLogger(__name__)
from botocore.exceptions import ClientError

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)


def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.5
    )
    return response.choices[0].message.content


def invoke_mistral(client, prompt):

    try:
        model_id = "mistral.mistral-7b-instruct-v0:2"
        body = {
            "prompt": prompt,
            "max_tokens": 200,
            "temperature": 0.5,
        }
        response = client.invoke_model(
            modelId=model_id, body=json.dumps(body)
        )
        response_body = json.loads(response["body"].read())
        outputs = response_body.get("outputs")

        completions = [output["text"] for output in outputs]

        return completions

    except ClientError:
        logger.error("Couldn't invoke Mistral 7B")
        raise


def generate_summary(conversation_list, summary_type, model_choice):

    client = boto3.client('bedrock-runtime', region_name='us-west-2')

    username = ""
    messages_text = ""
    #for conversation in conversation_list:
    #    if 'message_text' in conversation:
    #        message_text = json.loads(conversation['message_text'])


    messages = [conversation.get('message_text', '')
                for conversation in conversation_list]

    messages_text = '\n'.join(messages)
    #username = list(messages_text.keys())[0]
    #messages_text += f"{username}: {messages_text[username]}\n"

    #message_text = conversation['message_text']
    # Extracting the username and message from the string representation of the dictionary
    username_start = messages_text.find("'") + 1
    username_end = messages_text.find("'", username_start)
    username = messages_text[username_start:username_end]

    print(messages_text)

    prompt = generate_summary_prompts(messages_text, summary_type, username)

    if model_choice == 'OPENAI':
        response = get_completion(prompt)
        return response

    elif model_choice == "Mistral":
        response = invoke_mistral(client, prompt)
        return response



def generate_summary_prompts(messages_text, summary_type, username):
    prompt = ""
    if summary_type == 'List':
        prompt = f"""
        A conversation is provided below between {username} and "Pi bot", delimited by triple quotes,
        your task is to extract the relevant information to generate summary.
    
        Please include relevant code snippets, links, and other important details 
        only if they contribute to the understanding of the topic.
    
        Perform following instructions:
    
        Step 1 - Review the conversation to understand the context and key points.
        Step 2 - Extract important information that adds value to the summary.
        Step 3 - Include code snippets, links, and other details judiciously.
        Step 4 - Generate a summary from the extracted information.
        Step 5 - Prioritize clarity and relevance in the generated summary.
        Step 6 - Format it as a numbered list.
        Step 7 - Return in the response format given below delimited by double quotes.
    
        ``` Conversation ```
        {messages_text}
        
        ``Response Format``
        ['username': username,
        'summary': summary]
        """

    elif summary_type == 'Bulleted List':
        prompt = f"""
            A conversation is provided below between {username} and "Pi bot", delimited by triple quotes,
            your task is to extract the relevant information to generate summary.
            Please include relevant code snippets, links, and other important details 
            only if they contribute to the understanding of the topic.
            Perform following instructions:
            Step 1 - Review the conversation to understand the context and key points.
            Step 2 - Extract important information that adds value to the summary.
            Step 3 - Include code snippets, links, and other details judiciously.
            Step 4 - Generate a summary from the extracted information.
            Step 5 - Prioritize clarity and relevance in the generated summary.
            Step 6 - Format it as a bulleted list.
            Step 7 - Return in the response format given below delimited by double quotes.
    
            ``` Conversation ```
            {messages_text}
            
            ``Response Format``
            ['username': username,
            'summary': summary]
            """

    elif summary_type == 'Paragraph':
        prompt = f"""
            A conversation is provided below between {username} and "Pi bot", delimited by triple quotes,
            your task is to extract the relevant information to generate summary.
            Please include relevant code snippets, links, and other important details 
            only if they contribute to the understanding of the topic.
            Perform following instructions:
            Step 1 - Review the conversation to understand the context and key points.
            Step 2 - Extract important information that adds value to the summary.
            Step 3 - Include code snippets, links, and other details judiciously.
            Step 4 - Generate a summary from the extracted information.
            Step 5 - Prioritize clarity and relevance in the generated summary.
            Step 6 - Format it as a paragraph.
            Step 7 - Return in the response format given below delimited by double quotes.
    
            ``` Conversation ```
            {messages_text}
            
            ``Response Format``
            ['username': username,
            'summary': summary]
            """

    elif summary_type == 'Table':
        prompt = f"""
            A conversation is provided below between {username} and "Pi bot", delimited by triple quotes,
            your task is to extract the relevant information to generate summary.
            Please include relevant code snippets, links, and other important details 
            only if they contribute to the understanding of the topic.
            Perform following instructions:
            Step 1 - Review the conversation to understand the context and key points.
            Step 2 - Extract important information that adds value to the summary.
            Step 3 - Include code snippets, links, and other details judiciously.
            Step 4 - Generate a summary from the extracted information.
            Step 5 - Prioritize clarity and relevance in the generated summary.
            Step 6 - Format it as a table.
            Step 7 - Return in the response format given below delimited by double quotes.
    
            ``` Conversation ```
            {messages_text}
            
            ``Response Format``
            ['username': username,
            'summary': summary]
            """

    return prompt