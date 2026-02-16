#SIT-AW  Copyright (C) CEA 2025  Razane Azrou
from .message_abstract import Message
import os 
from glob import glob
import base64

class Message_UC2(Message):

    def __init__(self,anomaly_case_path,sys_prompt:str,prompt:str,local_model:bool):
        super().__init__(anomaly_case_path,sys_prompt,prompt,local_model)

    def get_uc_specific_message(self):
        
        messages = self.get_user_message()
        scan_path = glob(os.path.join(self.anomaly_case_path,"**/zivid_*.png"))
        if len(scan_path) == 0:
            raise Exception(f"You need a scan image for UC2, the path : {scan_path}, may be incorrect")
        else:
            scan_path = scan_path[0]

        if not self.local_model:
            with open(scan_path,"rb") as scan_file:
                base64_image = base64.b64encode(scan_file.read()).decode("utf-8")
                image = f"data:image/png;base64,{base64_image}"
                extra_message = {"type":"image_url","image_url":{"url": image}}
        else:
            image = scan_path
            extra_message = {"image":image}
                
        messages[1]["content"].append(extra_message)

        return messages
