import json
import time

from openai import OpenAI
import os
import base64


def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def response_save_to_json(data, filename):
    with open(filename, 'a', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_response(API_Key, text_input, image_base64_url,i,temperature,image_name):
    model="gpt-4o"
    response_data={
        "ID":i+1,
        "Temperature":temperature,
        "text_input":text_input,
        "image_name":image_name,
        "Long_response":None,
        "Short_response":None,
        "Long_response_timestamp":None,
        "Long_response_time":None,
        "Long_response_Usage": {},
        "Short_response_timestamp": None,
        "Short_response_time":None,
        "Short_response_Usage": {}
    }
    client=OpenAI(
        base_url="https://api.gptsapi.net/v1",
        api_key=API_Key
    )
    requests = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": text_input
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64_url}"
                    },
                },
            ],
        }
    ]
    start_time = time.time()
    response = client.chat.completions.create(
        model=model,
        messages=requests,
        # max_tokens = 200,
        temperature=temperature
    )
    end_time=time.time()
    long_response_time = end_time - start_time
    response_data["Long_response_time"]=long_response_time
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))
    response_data["Long_response_timestamp"]=timestamp
    long_response = response.choices[0].message.content
    response_data["Long_response"]=long_response
    usage = response.usage
    response_data["Long_response_Usage"]={
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "total_tokens": usage.total_tokens
    }
    '''
        "completion_tokens_details": {
            "reasoning_tokens": usage.completion_tokens_details.reasoning_tokens,
            "accepted_prediction_tokens": usage.completion_tokens_details.accepted_prediction_tokens,
            "rejected_prediction_tokens": usage.completion_tokens_details.rejected_prediction_tokens
        }
        '''


    start_time=time.time()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "assistant", "content": long_response},
            {"role": "user",
             "content":"Provide only the option content without adding any explanation or extra content: which option does this content refer to?"
             #"content": "Answer with the shortest possible phrase: which option is the most likely answer?"
            }
        ],
        temperature=temperature
    )
    end_time=time.time()
    short_response_time=end_time-start_time
    response_data["Short_response_time"]=short_response_time
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))
    response_data["Short_response_timestamp"]=timestamp
    short_response = response.choices[0].message.content
    response_data["Short_response"]=short_response
    usage = response.usage
    response_data["Short_response_Usage"]={
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "total_tokens": usage.total_tokens
    }
    '''
            "completion_tokens_details": {
                "reasoning_tokens": usage.completion_tokens_details.reasoning_tokens,
                "accepted_prediction_tokens": usage.completion_tokens_details.accepted_prediction_tokens,
                "rejected_prediction_tokens": usage.completion_tokens_details.rejected_prediction_tokens
            }
            '''

    return response_data

def get_text_input(json_data):
    qusetion=json_data["question describe"]
    options = [opt["option"] for opt in json_data["options"]]
    text_input=f"Question:{qusetion}\nOptions:\n"+"\n".join(options)
    option_text="\n".join(options)
    return text_input,option_text

def get_cases_input(json_file, image_folder):
    cases_input=[]
    options=[]
    images=[]
    with open(json_file, 'r', encoding='utf-8') as file:
        json_datas = json.load(file)
        for i in range(0,len(json_datas)):
            json_data=json_datas[i]
            case_text_input,option_text=get_text_input(json_data)
            image_name=json_data["image name"]
            image_path=os.path.join(image_folder,image_name)
            if not os.path.exists(image_path):
                print(image_name,"不存在")
                continue
            image_base64_url=encode_image(image_path)
            cases_input.append([case_text_input,image_base64_url])
            option=json_data["options"]
            options.append(option)
            image=json_data["image name"]
            images.append(image)
    return cases_input,images

#使用api对pretest的60个case进行测试
json_file="textdata/NEJM.json"
image_folder="image/NEJM"
output_json="output/NEJM/none role-play/NEJM_output_tem0.json"
API_Key="your api key"
#role_play_text="Suppose you are a medical expert and have very rich medical knowledge. As a medical student, I would like to ask you such a question.\n"
cases_input,images=NEJM_ChatGPT_get_response.get_cases_input(json_file,image_folder)
temperature=0
for i in range(0,len(cases_input)):
    #case_text_input = role_play_text + cases_input[i][0]
    case_text_input=cases_input[i][0]
    case_image_input=cases_input[i][1]
    response_data=NEJM_ChatGPT_get_response.get_response(API_Key,case_text_input,case_image_input,i,temperature,images[i])
    NEJM_ChatGPT_get_response.response_save_to_json(response_data,output_json)
    time.sleep(5)

