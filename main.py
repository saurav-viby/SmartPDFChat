import openai
import os
import uvicorn
import json
import requests
from fastapi import FastAPI, HTTPException,Request as rr
from pydantic import BaseModel
from langchain import PromptTemplate
from langchain.llms import OpenAI


aikey = json.load(open("/var/run/secrets/openai-credentials"))
AI_API_KEYS = aikey['KEY_API']
openai_api_key = os.environ.get('OPENAI_API_KEY', AI_API_KEYS)
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set. Please set the API key in your environment.")
os.environ['OPENAI_API_KEY'] = openai_api_key

llm = OpenAI(temperature=0.4,max_tokens=800)

app = FastAPI()



template =""" You are ChatGPT, a large language model trained by OpenAI.You must always provide a response.
what are the perscription details in the {subject}?
show the answer in array like key value pair.
The answer should be strictly follow this example :
{{{{Drug Name :D RISE CAPSULE 60000 IU/(),Dosage:60000IU, Route: ORAL, Frequency (M-A-E-N):MONTHLY ONCE,Duration:3 Months,Drug Instruction:AFTER FOOD}}}},
{{{{Drug Name:SHELCAL TABLET 500,Dosage:60000IU, Route: ORAL, Frequency (M-A-E-N):0-1-0-0,Duration:3 Months,Drug Instruction:null}}}},
"""
template2=""" 
You are ChatGPT, a large language model trained by OpenAI.You must always provide a response.
what are the Blood Test details in the {blood_test}?
example for Blood Test Results :
{{{{test:Haemoglobin (g/dL),result:22.1}}}},
{{{{test:platelet (/µL),result:null}}}},
"""

template3="""
You are ChatGPT, a large language model trained by OpenAI.You must always provide a response.

Question:What is the {question} in {subject2} ?

The answer should be showed in key value pair like an array sperated by curly braces .

If no exact answer found, you should show 'Not mentioned' against the question.

The answer should be strictly follow this example and does not contain any answer tag just the data like the example:
example-
{{UHID: 12018136222}},{{Body Temperature: 36.6 C}},{{Pulse Rate: 82 beats/min}},{{Blood Pressure: 132~82 mm/Hg}},{{Respiration: 20 breaths/min}},{{SPO2: 100 %}},{{BMI: 23.96 kg/m2}},{{Weight: 53.2 kg}},{{Height: 149 cm}}
"""

template4="""
You are ChatGPT, a large language model trained by OpenAI.You must always provide a response.

Question: {question}

The livespace-id , user-id and collection-id should be same.

Based on the question add only relevant columns   accordingly shown in example format
Example :   data = {{

        'args[livespace-id]': 372,
'args[columns][0]': '',
'args[user-id]': 353,
'op': 'livespace.spreadsheet.create',
'args[name]': 'studentdata',
'args[collection-id]': 0,
'args[description]':'',
}}
"""





conversation = [{"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI."}]

@app.post("/chat/")
async def chat_with_ai(request: rr):
    data = await request.json()
    input_message = data['message']
    input_query = data['query']
    


    if input_query == "prescription":
        if "prescription" in input_message.lower():
            promt_template = PromptTemplate(
                input_variables=['subject'], template=template)
            response = llm(promt_template.format(subject=input_message))
            return {"bot_reply": response}
        else:
            return{"bot_reply":[""]}
        
    elif input_query == "blood_test":
        if "blood test" in input_message.lower():
            promt_template2 = PromptTemplate(
                input_variables=['blood_test'], template=template2)
            response = llm(promt_template2.format(blood_test=input_message))
            return {"bot_reply": response}
        else:
            return{"bot_reply":[""]}
    else:
        promt_template2 = PromptTemplate(
            input_variables=['question','subject2'], template=template3)
        response = llm(promt_template2.format(question=input_query,subject2=input_message))
        return {"bot_reply": response}

   # print(response)

    return {"bot_reply": response}

@app.post("/ss_chat/")
async def ss_chat(request: rr):
    data = await request.json()
    input_query = data['query']
    print(input_query)
    if input_query !=None:
        promt_template = PromptTemplate(
            input_variables=['question'], template=template4)
        responsedata = llm(promt_template.format(question=input_query))
        print(responsedata)
        responsedata=data
       # print(type(data))
        # return  responsedata
        

        headers = {
            "Authorization": "Basic xxxxxxx"  # Replace with your actual access token
        }
        php_api_url = ""

   

        response = requests.post(php_api_url, data=data,headers=headers)
        print(response)

        if response.status_code == 200:

            php_data = response.json()
            # Process the JSON data
            return php_data
        else:
            # Handle error cases
            return {"error": "Something went wrong with the PHP API"}
if __name__ == "__main__":
    
    uvicorn.run(app, host="0.0.0.0", port=80)
