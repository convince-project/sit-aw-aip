#SIT-AW  Copyright (C) CEA 2025  Razane Azrou
from .message_abstract import Message

class Message_UC1(Message):

    def __init__(self,anomaly_case_path,uc_message_specification,sys_prompt:str,prompt:str):
        super().__init__(anomaly_case_path,uc_message_specification,sys_prompt,prompt)

    def get_uc_specific_message(self):
        
        messages = self.get_user_message()

        return messages
