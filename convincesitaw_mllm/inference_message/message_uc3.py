#SIT-AW  Copyright (C) CEA 2025  Razane Azrou
from .message_abstract import Message
from glob import glob
import os 
import base64
from warnings import warn

class Message_UC3(Message):

    def __init__(self,anomaly_case_path:str,sys_prompt:str,prompt:str,local_model:bool):
        super().__init__(anomaly_case_path,sys_prompt,prompt,local_model)

    def get_uc_specific_message(self):
        
        messages = self.get_user_message(freq=100)
        #navigation status evolution + interaction if any
        txt_path = glob(os.path.join(self.anomaly_case_path,"text_files/*.txt"))
        if len(txt_path) == 0:
            raise Exception(f"You need a txt file for UC3, the path : {self.anomaly_case_path}, may be incorrect or missing the text_files folder.")
        else:
            for txt_file in txt_path:
                with open(txt_file) as file:
                    text = file.read()
                messages[1]["content"].append({"type":"text","text":text})

        spectograms_files = glob(os.path.join(self.anomaly_case_path,"audio_images_files/*.png"))
        if len(spectograms_files) == 0:
            warn(f"You may need audio mel spectograms images for UC3, the path : {spectograms_files}, is empty")
        else: 
            for mel_spec in spectograms_files: 
                if not self.local_model:
                    with open(mel_spec,"rb") as scan_file:
                        base64_image = base64.b64encode(scan_file.read()).decode("utf-8")
                        image = f"data:image/png;base64,{base64_image}"
                        extra_message = {"type":"image_url","image_url":{"url": image}}
                else:
                    extra_message = {"image":mel_spec}
                
                messages[1]["content"].append(extra_message)

        return messages
