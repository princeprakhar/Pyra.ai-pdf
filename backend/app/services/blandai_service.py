from app.config import BLANDAI_API_KEY
from app.utils.system_prompt  import SystemPrompt_V1
from fastapi import Request,HTTPException # type: ignore
import requests
from rich import print
import logging


def make_call(
    objective: str,
    context: str,
    caller_number: str,
    caller_name: str,
    caller_email: str,
    phone_number: str,
    language_code: str,
    name_of_org: str
):
    try:
        url = "https://api.bland.ai/v1/calls"
        headers = {
            "authorization": f"{BLANDAI_API_KEY}",
            "Content-Type": "application/json"
        }

        # Instantiating SystemPrompt_V1 with the validated payload attributes
        system_prompt = SystemPrompt_V1(
            objective=objective,
            context=context,
            caller_number=caller_number,
            caller_name=caller_name,
            caller_email=caller_email,
            name_of_org=name_of_org
        )
        # Generate system prompt message
        system_prompt_text = system_prompt.generate_system_message_assistant()

        payload_dict = {
            "phone_number": phone_number,
            "task": system_prompt_text,  
            "voice": "443b01cf-3123-4e22-9c92-03cf10d897d9",
            "background_track": None,
            "wait_for_greeting": True,
            "block_interruptions": False,
            "interruption_threshold": 70,
            "language": language_code,
            "noise_cancellation": True,
            "ivr_mode": True,
            "model": "base",
            "temperature": 0.8,
            "record": False,
        }

        logging.info(f"Making request to Bland AI with payload: {payload_dict}")
        response = requests.post(url, json=payload_dict, headers=headers)
        
        if response.status_code != 200:
            logging.error(f"Bland AI API error: {response.status_code} - {response.text}")
            raise HTTPException(status_code=response.status_code, detail=f"Bland AI API error: {response.text}")
            
        return response.json()
        
    except ValueError as e:
        logging.error(f"Value error in make_call: {str(e)}")
        raise HTTPException(status_code=422, detail=f"Invalid request data: {str(e)}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error in make_call: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error calling external API: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error in make_call: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
