#SIT-AW  Copyright (C) CEA 2025  Razane Azrou
from .message_abstract import Message
from glob import glob
import os 

class Message_UC3(Message):

    def __init__(self,anomaly_case_path:str,sys_prompt:str,prompt:str,local_model:bool):
        super().__init__(anomaly_case_path,sys_prompt,prompt,local_model)

    def get_uc_specific_message(self):
        
        messages = self.get_user_message(freq=10)
        ##will probably need to add navigation and other data not in csv_images, images and video

        return messages
