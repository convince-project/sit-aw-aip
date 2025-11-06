#SIT-AW  Copyright (C) CEA 2025  Razane Azrou
from .message_abstract import Message
import os 
from glob import glob

class Message_UC2(Message):

    def __init__(self,anomaly_case_path,uc_message_specification,sys_prompt:str,prompt:str):
        super().__init__(anomaly_case_path,uc_message_specification,sys_prompt,prompt)

    def get_uc_specific_message(self):
        
        messages = self.get_user_message()
        scan_path = glob(os.path.join(self.anomaly_case_path,"**/*.png"))[0]
        if not scan_path:
            raise Exception(f"You need a scan image for UC2, the path : {scan_path}, may be incorrect")
        
        messages[1] = self.uc_message_specification.extra_message(scan_path,message=messages[1])

        return messages
