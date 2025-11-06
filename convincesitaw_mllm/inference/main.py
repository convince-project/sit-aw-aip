#SIT-AW  Copyright (C) CEA 2025  Razane Azrou
from litellm import completion
from convincesitaw_mllm.prompts import user_prompts
from convincesitaw_mllm.inference.Ucs_mapping import use_case_map,use_case_prompt_map,message_callback_map
from convincesitaw_mllm.inference_message.message_abstract import Message
from dataclasses import dataclass

@dataclass
class Inference:
    
    use_case_id:int
    anomaly_case_path : str
    model_id : str
    distant_server_ip : str 
    port : str
   
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

    def get_use_case(self,sys_prompt=None):

        use_case = use_case_map[self.use_case_id]
        message_callback = message_callback_map[self.use_case_id]

        if not sys_prompt:
            sys_prompt = use_case_prompt_map[self.use_case_id]
            
        prompt1 = user_prompts.USER_PROMPT1
        prompt2 = user_prompts.USER_PROMPT2
        messages = message_callback(anomaly_case_path=self.anomaly_case_path,uc_message_specification=use_case,
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

