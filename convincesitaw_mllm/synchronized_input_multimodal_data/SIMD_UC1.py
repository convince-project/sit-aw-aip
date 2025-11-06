#SIT-AW  Copyright (C) CEA 2025  Razane Azrou
from glob import glob
import os 
from .SIMD_abstract import SIMD
import pandas as pd
import numpy as np
import json
from spatialmath.base import qnorm,qqmul
import base64
import ast

class UC1(SIMD):

    def __init__(self):
        super().__init__()

    def statistics_to_get(self,array:np.array,boolean_not_numeric:bool):

        if boolean_not_numeric:
            redundancy = array[array == 1]
            indexes = np.where(array==1)
            return redundancy,indexes
        if array.shape[1] <= 3:
            mean = array.mean(axis=0)
            std = array.std(axis=0)
            return {"mean":mean,"std":std}
        else : #should be quaternions
            q_sum = np.sum(array,axis=0)
            q_norm_sum = 0
            for q in array:
                q_norm_sum += qnorm(q)
            q_mean = q_sum/q_norm_sum
            variance = 0
            for q in array :
                d_geodesic = (1/np.pi)*np.arccos(qqmul(q_mean,q))
                variance += d_geodesic**2
            variance /= array.shape[0]
            return {"mean":q_mean,"std":np.sqrt(variance)}
        
    def transform_str_to_numbers(self,data:pd.Series):
        return data.apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    
    def proprio_statistics(self,data_frame:pd.DataFrame,samples_nb:int) -> dict :

        statistics_dict = {} 

        boolean_not_numeric = False
        if data_frame.shape[1] <= 2: #for me this means there is timestamps + boolean data --> but I will need to find a common formatting of input data
            boolean_not_numeric= True

        for col in data_frame.columns[1:]:
            samples = []
            data_frame.loc[:,col] = self.transform_str_to_numbers(data_frame[col])
            array = np.array(data_frame[col].to_list())
           
            samples.append(array[0])
            for i in range(1,array.shape[0]-2,array.shape[0]//samples_nb):
                samples.append(array[i])
            samples.append(array[-1])
            
            statistics = self.statistics_to_get(array=array,boolean_not_numeric=boolean_not_numeric)
            if boolean_not_numeric:
                if statistics[0].shape[0] != 0:
                    occurrences = np.array(data_frame[data_frame.columns[0]].to_list())[statistics[1]]
                    duration = occurrences[-1]-occurrences[0]
                    dict_entry = {"duration":duration,"redundancy":np.sum(statistics[0],dtype=float)}
                else:
                    dict_entry = {"duration":"No occurrence","redundancy":0.0}
            else:
                dict_entry = statistics
            
            dict_entry['samples'] = samples
            statistics_dict[col] = dict_entry

        return statistics_dict
    

    def get_chunked_images_dict(self,frames,images_chunk_size):

        images_dict = {}
        for rec, iteration in enumerate(range(0,len(frames),images_chunk_size)):
            chunk_dict = {}
            for i in range(images_chunk_size):
                with open(frames[iteration],"rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode("utf-8")
                    image_url = f"data:image/png;base64,{base64_image}"
                chunk_dict[f"sample{i}"] = image_url
            images_dict[f"image_chunk_{rec}"] = chunk_dict
        return images_dict

    def message_content_per_chunk(self,message,json_path:str,chunk_index:int):
        with open(f"{json_path}/data_chunk_{chunk_index}.json","r") as chunk_file :
            chunk = json.load(chunk_file)

            text = f"""
            Time : {chunk_index} second
            Odometry :
                Robot's position given by odometry : 
                    mean : {chunk[f"proprio_chunk{chunk_index}"][f"odometrie_data_chunk{chunk_index}"]["Pose position"]["mean"]},
                    std : {chunk[f"proprio_chunk{chunk_index}"][f"odometrie_data_chunk{chunk_index}"]["Pose position"]["std"]},
                    samples : {chunk[f"proprio_chunk{chunk_index}"][f"odometrie_data_chunk{chunk_index}"]["Pose position"]["samples"]}

                Robot's orientation given by odometry :
                    mean : {chunk[f"proprio_chunk{chunk_index}"][f"odometrie_data_chunk{chunk_index}"]["Pose orientation"]["mean"]},
                    std : {chunk[f"proprio_chunk{chunk_index}"][f"odometrie_data_chunk{chunk_index}"]["Pose orientation"]["std"]},
                    samples : {chunk[f"proprio_chunk{chunk_index}"][f"odometrie_data_chunk{chunk_index}"]["Pose orientation"]["samples"]}
                 
                Robot's linear velocity given by odometry :  
                    mean : {chunk[f"proprio_chunk{chunk_index}"][f"odometrie_data_chunk{chunk_index}"]["Twist linear"]["mean"]},
                    std : {chunk[f"proprio_chunk{chunk_index}"][f"odometrie_data_chunk{chunk_index}"]["Twist linear"]["std"]},
                    samples : {chunk[f"proprio_chunk{chunk_index}"][f"odometrie_data_chunk{chunk_index}"]["Twist linear"]["samples"]}
               
                Robot's angular velocity given by odometry :
                    mean : {chunk[f"proprio_chunk{chunk_index}"][f"odometrie_data_chunk{chunk_index}"]["Twist angular"]["mean"]},
                    std : {chunk[f"proprio_chunk{chunk_index}"][f"odometrie_data_chunk{chunk_index}"]["Twist angular"]["std"]},
                    samples : {chunk[f"proprio_chunk{chunk_index}"][f"odometrie_data_chunk{chunk_index}"]["Twist angular"]["samples"]}
                    
            IMU :
                Linear acceleration : 
                    mean : {chunk[f"proprio_chunk{chunk_index}"][f"imu_data_data_chunk{chunk_index}"]["Linear Acceleration"]["mean"]},
                    variance : {chunk[f"proprio_chunk{chunk_index}"][f"imu_data_data_chunk{chunk_index}"]["Linear Acceleration"]["std"]},
                    samples : {chunk[f"proprio_chunk{chunk_index}"][f"imu_data_data_chunk{chunk_index}"]["Linear Acceleration"]["samples"]}
             
            Clif sensor :
                Duration : {chunk[f"proprio_chunk{chunk_index}"][f"clif_sensors_data_chunk{chunk_index}"]["Data"]["duration"]},
                Redundancy : {chunk[f"proprio_chunk{chunk_index}"][f"clif_sensors_data_chunk{chunk_index}"]["Data"]["redundancy"]},
                samples : {chunk[f"proprio_chunk{chunk_index}"][f"clif_sensors_data_chunk{chunk_index}"]["Data"]["samples"]}
            Wheel lift : 
                Duration : {chunk[f"proprio_chunk{chunk_index}"][f"wheel_lift_data_chunk{chunk_index}"]["Data"]["duration"]},
                Redundancy : {chunk[f"proprio_chunk{chunk_index}"][f"wheel_lift_data_chunk{chunk_index}"]["Data"]["redundancy"]},
                samples : {chunk[f"proprio_chunk{chunk_index}"][f"wheel_lift_data_chunk{chunk_index}"]["Data"]["samples"]}

            """
            text_msg = {"type":"text","text":text}
            message["content"].append(text_msg)
            for image in chunk[f"image_chunk_{chunk_index}"].values():
                image_msg = {"type":"image_url","image_url":{"url": image}}
                message["content"].append(image_msg)
            
        return message


    def get_data_name(self,excel_file:str):

        name = excel_file.split("/")[-1] #get data name
        name = name.split(".")[0] #remove extension
        
        return name

    def main(self,root_path:str):

        data_folders = glob(root_path+"/*")
        anomaly_iteration = 0
        for anomaly in data_folders:
            anomaly_path = os.path.join(root_path,anomaly)
            #All proprioception data
            excel_folder = os.path.join(anomaly_path,"excel_files")
            excel_files = glob(excel_folder+"/*")
            proprio_dict = {}
            for excel_file in excel_files:
                data_frame = pd.read_excel(excel_file,usecols=lambda x: "covariance" not in x)
                data_frame = data_frame.rename(columns={"Unnamed: 0":"timestamp"})
                data_name = self.get_data_name(excel_file)
                chunked_dict = self.get_proprio_dict(data_name,data_frame,samples_nb=5)
                
                proprio_dict[f"{data_name}_{anomaly_iteration}"] = chunked_dict

            images_folder = os.path.join(anomaly_path,"images")
            images = glob(images_folder+"/*.png")
            total_time = 10 
            images_chunkes = len(images)//total_time
            images_dict = self.get_chunked_images_dict(images,images_chunkes)
         
            json_save_root_path = os.path.join(anomaly_path,f"json_files")
            if not os.path.isdir(json_save_root_path):
                os.mkdir(json_save_root_path)
            
            self.get_json_files(proprio_dict,images_dict,json_save_root_path)
            
