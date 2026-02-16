#SIT-AW  Copyright (C) CEA 2025  Razane Azrou
from .message_abstract import Message
from glob import glob
import os 

class Message_UC1(Message):

    def __init__(self,anomaly_case_path:str,sys_prompt:str,prompt:str,local_model:bool):
        super().__init__(anomaly_case_path,sys_prompt,prompt,local_model)

    def get_uc_specific_message(self):
        
        messages = self.get_user_message()
        txt_path = glob(os.path.join(self.anomaly_case_path,"text_files/*.txt"))
        if len(txt_path) == 0:
            raise Exception(f"You need a txt file for UC1, the path : {self.anomaly_case_path}, may be incorrect or missing the text_files folder.")
        else:
            txt_path = txt_path[0]

        with open(txt_path) as file:
            text = file.read()

        messages[1]["content"].append({"type":"text","text":text})

        return messages
