import json
import time
from lib2to3.fixes.fix_input import context

from openai import OpenAI
import os
import base64


def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def response_save_to_json(data, filename):
    with open(filename, 'a', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_response(API_Key, text_input, images_base64_url,i,temperature,images_name):
    model="gpt-4o"
    response_data={
        "ID":i+1,
        "Temperature":temperature,
        "text_input":text_input,
        "image_name":images_name,
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
                }
            ]
        }
    ]

    for image_base64_url in images_base64_url:
        requests[0]["content"].append(
            {
                "type": "image_url",
                "image_url": {
                "url": f"data:image/jpeg;base64,{image_base64_url}"
                }
            }

        )
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
    options =[]
    for opt in json_data["options"]:
        options.append(opt)
    text_input=f"Question:{qusetion}\nOptions:\n"+"\n".join(options)
    return text_input

def get_cases_input(json_file, image_folder):
    cases_input=[]
    images=[]
    with open(json_file, 'r', encoding='utf-8') as file:
        json_datas = json.load(file)
        for i in range(0,len(json_datas)):
            json_data=json_datas[i]
            case_text_input=get_text_input(json_data)
            case_images=json_data["image"]
            images_name=[]
            images_base64_url=[]
            for i in range(0,len(case_images)):
                image_name=case_images[i]["image name"]
                images_name.append(image_name)
                image_path=os.path.join(image_folder,image_name)
                if not os.path.exists(image_path):
                    print(image_name, "不存在")
                    continue
                image_base64_url=encode_image(image_path)
                images_base64_url.append(image_base64_url)
            cases_input.append([case_text_input,images_base64_url])
            images.append(images_name)
    return cases_input,images


json_file="textdata/Lancet.json"
image_folder="image/Lancet"
#修改输出文件
output_json="output/Lancet/none role-play/Lancet_output_tem1.json"
API_Key="your api key"
#role_play_text="Suppose you are a medical expert and have very rich medical knowledge. As a medical student, I would like to ask you such a question.\n"
cases_input,images=get_cases_input(json_file,image_folder)
temperature=1
for i in range(0,len(cases_input)):
    #case_text_input = role_play_text + cases_input[i][0]
    case_text_input=cases_input[i][0]
    case_image_input=cases_input[i][1]
    response_data=get_response(API_Key,case_text_input,case_image_input,i,temperature,images[i])
    response_save_to_json(response_data,output_json)
    time.sleep(20)
