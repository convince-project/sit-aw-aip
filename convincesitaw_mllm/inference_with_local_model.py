from convincesitaw_mllm.inference.main import Inference
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor, BitsAndBytesConfig
import tyro
import os

def main(use_case_id:int,anomaly_case_path:str,system_prompt:str=""):

    #this will be charge each time.
    #to avoid it the code can be changed into creating a thred for this and making model and processor varibales accessible to the threads that uses them
    model_path = "Qwen/Qwen2.5-VL-7B-Instruct"

    # Create quantization config
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,  # or load_in_4bit=True for 4-bit quantization
    )

    # Load quantized model
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        model_path,
        quantization_config=bnb_config,
        device_map="auto",
        # Note: don't force torch_dtype here when using bitsandbytes quantization
    )

    processor = AutoProcessor.from_pretrained(model_path)

    inference = Inference(use_case_id=use_case_id,anomaly_case_path=anomaly_case_path,model_id=None,distant_server_ip=None,port=None)
    messages,prompt2 = inference.get_use_case(system_prompt,local_model=True)

    print('done init####################')
    
    reply1 = inference.inference_with_local_model(model,processor,messages)
    print('done first inference ################')
    messages.append({"role":"assistant","content":reply1})
    messages.append({"role":"user","content":prompt2})
    reply2 = inference.inference_with_local_model(model,processor,messages)
    print('done second inference ################')

    print('##########################################')
    print('##########################################')
    print(reply1)
    print(reply2)

    return messages,inference,reply2,model,processor

def cli():
    tyro.cli(main)
