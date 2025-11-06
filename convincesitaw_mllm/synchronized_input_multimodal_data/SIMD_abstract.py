#SIT-AW  Copyright (C) CEA 2025  Razane Azrou
import numpy as np                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              
import pandas as pd
import json
from abc import ABC, abstractmethod


class SIMD(ABC):
    
    def __init__(self):
        return  

    @abstractmethod
    def statistics_to_get(self):
       pass

    @abstractmethod
    def proprio_statistics(self) -> dict :
       pass
    
    @abstractmethod
    def get_chunked_images_dict(self):
        pass
    
    @abstractmethod
    def message_content_per_chunk(self):
        pass

    @abstractmethod
    def main(self,rootpath:str):
        pass

    def get_proprio_dict(self,data_name:str,data_frame:pd.DataFrame,samples_nb:int):

        time = np.sort(data_frame["timestamp"].to_numpy())
        time = time -time[0]
        data_frame["timestamp"] = time

        chunked_dict = {}
        for i in range(1,round(time[-1])+1):
            data_f_h = data_frame["timestamp"] <= i
            data_f_l = data_frame["timestamp"] >= i-1
            data_f = data_frame[data_f_h & data_f_l]
            statistics_dict = self.proprio_statistics(data_f,samples_nb)
            chunked_dict[data_name+f"_chunk{i-1}"] = statistics_dict
        
        return chunked_dict

    def get_json_files(self,proprio_dict:dict,images_dict:dict,json_save_path:str):

        class NpEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, np.integer):
                    return int(obj)
                if isinstance(obj, np.floating):
                    return float(obj)
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                return super(NpEncoder, self).default(obj)
            

        higher_im_index = False
        for key_im,val_im in images_dict.items():
            proprio = {}
            index = int(key_im.split("_")[-1])
            for _,val_proprio in proprio_dict.items():
                keys_list = list(val_proprio.keys())
                if index >= len(keys_list):
                    higher_im_index = True
                    break
                proprio[keys_list[int(index)]] = val_proprio[keys_list[int(index)]]
            if higher_im_index:
                break
            with open(f"{json_save_path}/data_chunk_{index}.json","w") as json_file:
                data_dict = {key_im:val_im,f"proprio_chunk{index}":proprio}
                json.dump(data_dict,json_file,indent=4,cls=NpEncoder)

    
