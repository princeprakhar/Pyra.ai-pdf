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


def end_call(call_id: str):
    try:
        url = f"https://api.bland.ai/v1/calls/{call_id}/stop"
        print(f"Url ----- {url}")
        headers = {
            "authorization": BLANDAI_API_KEY,  # docs don’t mention "Bearer"
            "Content-Type": "application/json"      
        }
        payload = {"call_id": call_id}

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            logging.error(f"Bland AI API error on end_call: {response.status_code} - {response.text}")
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Bland AI API error: {response.text}"
            )
        return response.json()

    except requests.exceptions.RequestException as e:
        logging.error(f"Request error in end_call: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error calling external API: {str(e)}")

    except Exception as e:
        logging.error(f"Unexpected error in end_call: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")



def get_call_status(call_id: str):
    try:
        url = f"https://api.bland.ai/v1/calls/{call_id}"
        headers = {
            "authorization": f"{BLANDAI_API_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            logging.error(f"Bland AI API error on get_call_status: {response.status_code} - {response.text}")
            raise HTTPException(status_code=response.status_code, detail=f"Bland AI API error: {response.text}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error in get_call_status: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error calling external API: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error in get_call_status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
def get_call_transcript(call_id: str):
    try:
        url = f"https://api.bland.ai/v1/calls/{call_id}/transcript"
        headers = {
            "authorization": f"{BLANDAI_API_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)   
        if response.status_code != 200:
            logging.error(f"Bland AI API error on get_call_transcript: {response.status_code} - {response.text}")
            raise HTTPException(status_code=response.status_code, detail=f"Bland AI API error: {response.text}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error in get_call_transcript: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error calling external API: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error in get_call_transcript: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    

