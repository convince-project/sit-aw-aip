#SIT-AW  Copyright (C) CEA 2025  Razane Azrou
from litellm import completion
from convincesitaw_mllm.inference.Ucs_mapping import use_case_map,use_case_prompt_map,message_callback_map
from convincesitaw_mllm.inference_message.message_abstract import Message
from dataclasses import dataclass
from torchvision import transforms
from qwen_vl_utils import process_vision_info 

@dataclass
class Inference:
    
    use_case_id:int
    anomaly_case_path : str
    model_id : str
    distant_server_ip : str|None
    port : str|None
   
    ## Works only with Qwen2.5VL -- need to adapt to other models
    def inference_with_local_model(self,model,processor,messages:Message):

        text = processor.apply_chat_template(messages,tokenize=False,add_generation_prompt=True)
        image, video_inputs, video_kwargs = process_vision_info(messages,image_patch_size=16, return_video_kwargs=True, return_video_metadata=True)
        transfo = transforms.Resize(size=(32,32))
        
        if video_inputs is not None:
            video_inputs, video_metadatas = zip(*video_inputs)
            video_inputs, video_metadatas = list(video_inputs), list(video_metadatas)
        else:
            video_metadatas = None
        
        images = []
        for im in image:
            ima  = transfo(im)
            images.append(ima)

        videos = []
        for video_nb in range(len(video_inputs)):
            video = transfo(video_inputs[video_nb])
            videos.append(video)

        inputs = processor(text=[text], images=images, videos=videos, padding=True, return_tensors="pt")
        inputs = inputs.to('cuda')

        output_ids = model.generate(**inputs, max_new_tokens=2048, temperature=1.0)
        generated_ids = [output_ids[len(input_ids):] for input_ids, output_ids in zip(inputs.input_ids, output_ids)]
        output_text = processor.batch_decode(generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True)
        return output_text[0]
    
    def inference_with_api(self,messages:Message):
        
        response = completion(
            model = self.model_id,
            messages = messages,
            api_base = f"{self.distant_server_ip}:{self.port}/v1",
            api_key="EMPTY",
            custom_llm_provider="openai",
            temperature = 0
        )
        return response.choices[0].message.content

    def get_use_case(self,sys_prompt:str="",local_model:bool=False):

        use_case_promts = use_case_prompt_map[self.use_case_id]
        message_callback = message_callback_map[self.use_case_id]

        if len(sys_prompt)==0:
            sys_prompt = use_case_promts.SYSTEM_PROMPT
            
        prompt1 = use_case_promts.USER_PROMPT1
        prompt2 = use_case_promts.USER_PROMPT2
        messages = message_callback(anomaly_case_path=self.anomaly_case_path,local_model=local_model,
                sys_prompt=sys_prompt,prompt=prompt1).get_uc_specific_message()

        return messages,prompt2

    def inference_with_hallucination_prevention(self,messages,critics_callback,*critics_args):
        
        #initialisation of critics loop verificators
        valid = False
        last_disagreement=''
        recidiv_detector = 0
        time_out = 0

        #critics loop for the first inference
        while valid == False and time_out< 5 :
            #to avoid criticing endlessly
            time_out += 1
            #inference call to the VLM API
            reply = self.inference_with_api(messages)

            #check if recidiv is detected
            if recidiv_detector > 2:
                print('recidiv detected')
                break

            #send the VLM response to the critics
            valid,disagreement = critics_callback(reply,*critics_args)

            #test critics validation and add disagreement to the user prompt
            if valid == False:
                print('Hallucination detected')
                print(f"disagrement statement : {disagreement}")
                disagreement = 'You previously responded this :"' +reply+'"\n'+ disagreement

                if last_disagreement == disagreement:
                    print('recidiv_detector updated')
                    recidiv_detector += 1
                else :
                    messages[1]['content'].append({"type":"text","text":disagreement})
            
            last_disagreement = disagreement
        
        return reply,messages

