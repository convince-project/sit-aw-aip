#SIT-AW  Copyright (C) CEA 2025  Razane Azrou
from glob import glob
from convincesitaw_mllm.synchronized_input_multimodal_data.SIMD_abstract import SIMD 
from dataclasses import dataclass
from abc import ABC, abstractmethod
import os

@dataclass
class Message(ABC):

    anomaly_case_path : str
    uc_message_specification : SIMD
    sys_prompt : str
    prompt : str

    def get_user_message(self):

        user_message = {
        "role":"user",
        "content" : []
        }

        json_path = os.path.join(self.anomaly_case_path,"json_files")
        nb_chunks = len(glob(json_path+"/*"))
        for chunk_index in range(nb_chunks):
            user_message = self.uc_message_specification.message_content_per_chunk(user_message,json_path,chunk_index)

        user_message["content"].append({"type":"text","text":self.prompt})
    
        messages = [
                {
                    "role": "system",
                    "content": [{"type":"text","text": self.sys_prompt}]
                },
                user_message,
            ]
        return messages


    @abstractmethod
    def get_uc_specific_message(self):
        pass
