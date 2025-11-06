#SIT-AW  Copyright (C) CEA 2025  Razane Azrou
from convincesitaw_mllm.inference.main import Inference
from critics.critics import critics_trigger_reply1,critics_trigger_reply2
import tyro
from dotenv import load_dotenv
import os

def main(use_case_id:int,anomaly_case_path:str,system_prompt:str=None):
    
    load_dotenv(dotenv_path="../.env")
    model = os.getenv("MODEL")
    IP = os.getenv("SERVER_IP")
    port = os.getenv("PORT")

    inference = Inference(use_case_id=use_case_id,anomaly_case_path=anomaly_case_path,model_id=model,distant_server_ip=IP,port=port)
    messages,prompt2 = inference.get_use_case(system_prompt)

    print('done init####################')
    
    if use_case_id == 2: #for now only this use case has critics
        reply1,messages = inference.inference_with_hallucination_prevention(messages,critics_trigger_reply1)
        print('done first inference ################')
        messages.append({"role":"assistant","content":reply1})
        messages.append({"role":"user","content":prompt2})
        reply2,_ = inference.inference_with_hallucination_prevention(messages,critics_trigger_reply2,(reply1))
        print('done second inference ################')
    
    else :
        reply1 = inference.inference_with_api(messages)
        print('done first inference ################')
        messages.append({"role":"assistant","content":reply1})
        messages.append({"role":"user","content":prompt2})
        reply2 = inference.inference_with_api(messages)
        print('done second inference ################')

    print('##########################################')
    print('##########################################')
    print(reply1)
    print(reply2)

    return messages,inference,reply2

def cli():
    tyro.cli(main)
