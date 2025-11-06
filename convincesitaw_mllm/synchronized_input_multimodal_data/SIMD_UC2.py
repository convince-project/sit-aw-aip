#SIT-AW  Copyright (C) CEA 2025  Razane Azrou
from glob import glob
import os 
from .SIMD_abstract import SIMD
import pandas as pd
import numpy as np
import base64
from torchvision.io import read_video
from torchvision import transforms
import ffmpeg
import json
from io import BytesIO

class UC2(SIMD):

    def __init__(self):
        super().__init__()

    def statistics_to_get(self,array:np.array,boolean_not_numeric:bool):

        '''
        if boolean_not_numeric:
            presence_indexes = np.where(array)[0]
            return presence_indexes
        '''
        mean = array.mean(axis=0)
        std = array.std(axis=0)
        
        return {"mean":mean,"std":std}

    def proprio_statistics(self,data_frame:pd.DataFrame,samples_nb:int) -> dict:

        statistics_dict = {}

        boolean_not_numeric = False
    
        for col in data_frame.columns[1:2]:
            samples = []
            array = np.array(data_frame[col].to_list()).astype(np.float64)

            samples.append(array[0])
            for i in range(1,array.shape[0]-2,array.shape[0]//samples_nb):
                samples.append(array[i])
            samples.append(array[-1])

            statistics = self.statistics_to_get(array=array,boolean_not_numeric=boolean_not_numeric)
            
            dict_entry = statistics
            
            dict_entry['samples'] = samples
            statistics_dict[col] = dict_entry
        return statistics_dict
    
    def convert_fromBytes_toPNG(self,pil_image):
         
        with BytesIO() as buffer:
            pil_image.save(buffer, format="PNG")
            buffer.seek(0)
            bs64_encoded = base64.b64encode(buffer.read()).decode("utf-8")
            image_url = f"data:image/png;base64,{bs64_encoded}"

        return image_url

    def get_chunked_images_dict(self,video_path,images_chunk_size,max_images_per_chunk):
      
        transform = transforms.ToPILImage()
        video= read_video(video_path,output_format="TCHW",pts_unit="sec")[0]
        images_dict = {}
        end = video.size(0)
        if max_images_per_chunk >= images_chunk_size:
            raise Exception("You can't for more images than the chunk size")
        im_freq = images_chunk_size//max_images_per_chunk
        for iteration in range(0,end,images_chunk_size):
            chunk_dict = {}
            for i in range(im_freq,images_chunk_size,im_freq):
                pil_image = transform(video[iteration])
                image_url = self.convert_fromBytes_toPNG(pil_image)
                chunk_dict[f"sample{i-im_freq}"] = image_url
            images_dict[f"image_chunk_{iteration//images_chunk_size}"] = chunk_dict
        
        return images_dict
        
    def extra_message(self,scan_path,message):

        with open(scan_path,"rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")
            image_url = f"data:image/png;base64,{base64_image}"

        image_msg = {"type":"image_url","image_url":{"url": image_url}}
        message["content"].append(image_msg)

        return message
    
    def message_content_per_chunk(self,message,json_path:str,chunk_index:int):
        with open(f"{json_path}/data_chunk_{chunk_index}.json","r") as chunk_file :
            chunk = json.load(chunk_file)
            text = f"""
            Time : {chunk_index} second
            Gripper jaws :
                Position : 
                    mean : {chunk[f"proprio_chunk{chunk_index}"][f"gripper_jaws_chunk{chunk_index}"]["position"]["mean"]},
            """
            text_msg = {"type":"text","text":text}
            message["content"].append(text_msg)
            for image in chunk[f"image_chunk_{chunk_index}"].values():
                image_msg = {"type":"image_url","image_url":{"url": image}}
                message["content"].append(image_msg)
            
        return message

    def get_video_data(self,video_file,total_time):

        video_metadata = ffmpeg.probe(video_file)["streams"][0]
        video_duration = round(float(video_metadata["duration"]))
        total_frames = int(video_metadata['avg_frame_rate'].split('/')[0])*video_duration
        images_chunks = total_frames//total_time

        return images_chunks

    
    def main(self,root_path):

        data_folders = glob(root_path+"/*")
        for anomaly_folder in data_folders:
            detected_anomaly = glob(anomaly_folder+"/*")
            proprio_dict = {}
            for data in detected_anomaly:
                csv_file = glob(data+"/*/*.csv")[0]
                data_frame = pd.read_csv(csv_file)
        
                gripper_data = data_frame[data_frame["name"] == "gripper_jaws"]
                try :
                    gripper_data_df = gripper_data.drop(["name","force","torque","presence"],axis=1)
                except:
                    gripper_data_df = gripper_data.drop(["name"],axis=1)
                chunked_dict = self.get_proprio_dict("gripper_jaws",gripper_data_df,samples_nb=5)


                proprio_dict["gripper_jaws"] = chunked_dict

                timestamp =gripper_data_df["timestamp"].to_numpy()
                total_time = round((timestamp - timestamp[0])[-1])
                video_file = glob(data+"/*/*_cam_video.mp4")[0]
            
                images_chunks = self.get_video_data(video_file,total_time)
                images_dict = self.get_chunked_images_dict(video_file,images_chunks,5)
                
                json_save_root_path = os.path.join(data,"json_files")
                if not os.path.isdir(json_save_root_path):
                    os.mkdir(json_save_root_path)

                self.get_json_files(proprio_dict,images_dict,json_save_root_path)
