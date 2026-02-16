#SIT-AW  Copyright (C) CEA 2025  Razane Azrou
from glob import glob
from dataclasses import dataclass,field
from abc import ABC, abstractmethod
import os
import base64

# don't hesitate to resize images if there are too many
@dataclass
class Message(ABC):

    anomaly_case_path : str
    sys_prompt : str
    prompt : str
    local_model : bool = False
    

    def get_user_message(self):
        
        user_message = {
        "role":"user",
        "content" : []
        }

        csv_images_graphs = os.path.join(self.anomaly_case_path,"csv_images_files")
        graphs_images = glob(csv_images_graphs+"/*")
        if len(graphs_images) == 0:
            raise Exception("It seems that the csv_images_files folder is empty or absent")
        if not self.local_model:
            images = glob(os.path.join(self.anomaly_case_path,"images")+"/*")
            if len(images) == 0:
                raise Exception("It seems that the images folder is empty or absent")
            # I can't sent videos to the server so I sent images 
            for image in images:
                with open(image,"rb") as file:
                    base64_image = base64.b64encode(file.read()).decode("utf-8")
                    visual_image = f"data:image/png;base64,{base64_image}"
                    user_message["content"].append({"type":"image_url","image_url":{"url": visual_image}})
            for graph_file in graphs_images:
                with open(graph_file,"rb") as graph:
                    base64_graph_image = base64.b64encode(graph.read()).decode("utf-8")
                    graph_image = f"data:image/png;base64,{base64_graph_image}"
                    user_message["content"].append({"type":"image_url","image_url":{"url": graph_image}})
        else:
            video = glob(os.path.join(self.anomaly_case_path,"video")+"/*")
            if len(video) == 0:
                raise Exception("It seems that the video folder is empty or absent")
            else:
                video = video[0]
            # It is possible to use videos locally
            user_message["content"].append({"video":video})
            for graph_file in graphs_images:
                user_message["content"].append({"image":graph_file})
           
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
