from fastapi import APIRouter, Depends, Body, HTTPException, status #type:ignore
from app.schemas import MakeCallRequest,CallDetailRequest 
from app.services.blandai_service import make_call
import logging
from rich import print #type:ignore


router  = APIRouter(prefix="/api/bland-ai",tags=["BlandAI"])
@router.post("/assistant-initiate-call")
async def make_call_route(request: MakeCallRequest):
    try:
        print(f"In the Make Call Route")
        objective = request.objective
        context = request.context
        caller_number = request.caller_number
        caller_name = request.caller_name
        caller_email = request.caller_email
        phone_number = request.phone_number
        language_code = request.language_code
        name_of_org = request.name_of_org
        print(request.__dict__)
        
        return make_call(
            objective=objective,
            context=context,
            caller_number=caller_number,
            caller_name=caller_name,
            caller_email=caller_email,
            phone_number=phone_number,
            language_code=language_code,
            name_of_org=name_of_org
        )
    except Exception as error:
        logging.error(f"Error in make_call_route: {error}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

# @router.post("/api/call-details")
# async def call_detail(request:CallDetailRequest):

#     try:
#         raw_data = await request.json()
#         call_id = raw_data['call_id']
#         caller_email = raw_data['caller_email']
#         url = f"https://api.bland.ai/v1/calls/{call_id}"
#         headers = {
#             "authorization": f"{Config.BLANDAI_API_KEY}",
#             "Content-Type": "application/json"
#         }
#         response = requests.request("GET", url, headers=headers)
#         response_dict = json.loads(response.text)
#         transcription_data = {"transcription": response_dict['concatenated_transcript']}

#         # Sending the mail to caller
#         mail_response = await mail_obj.send_email_call_details_async(caller_email,response_dict['summary'],response_dict['recording_url'])
#         if mail_response:
#             logging.info("Mail Sent succesfully")
#         return JSONResponse(transcription_data)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
