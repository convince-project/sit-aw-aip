#SIT-AW  Copyright (C) CEA 2025  Razane Azrou
from glob import glob
import os 
from .SIMD_abstract import SIMD
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # non-GUI backend
import matplotlib.pyplot as plt
import numpy as np
import shutil
import cv2

class UC2(SIMD):

    def __init__(self):
        super().__init__()
    
    def generate_images(self,video_file, images_path):

        cap = cv2.VideoCapture(video_file)
        frame_id = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            resized_image = cv2.resize(frame, (32, 32))
            output_path = os.path.join(images_path, f"frame_{frame_id:05d}.png")
            cv2.imwrite(output_path, resized_image)
            frame_id += 1

        cap.release()

    def csv_to_image(self,csv_file,image_save_path):

        data = pd.read_csv(csv_file)
        gripper_data = data[data["name"] == "gripper_jaws"]
        gripper_position = gripper_data["position"].to_numpy()
        gripper_position_time_stamps = gripper_data["timestamp"].to_numpy()
        gripper_position_time_stamps = gripper_position_time_stamps - gripper_position_time_stamps[0]

        lower_bound = np.array([0.04 for _ in range(gripper_position.size)])
            
        plt.plot(gripper_position_time_stamps,gripper_position)
        plt.plot(gripper_position_time_stamps,lower_bound)
        plt.xlabel("time(seconds)")
        plt.ylabel("gripper jaws position")
        plt.title("gripper jaws position's evolution in time")
        plt.savefig(image_save_path)
        plt.close()

    def graph_images(self,csv_file,csv_to_images_path):
      
        splitted_string = csv_to_images_path.split("/")
        graph_image_name = "graph_image_"+splitted_string[-1]+".png"
        graph_image_name = os.path.join(csv_to_images_path,graph_image_name)
        self.csv_to_image(csv_file,graph_image_name)

    def main(self,root_path):

        data_folders = glob(root_path+"/*")
        for anomaly_folder in data_folders:
            detected_anomaly = glob(anomaly_folder+"/*")

            for data in detected_anomaly:
                csv_file_list = glob(data+"/*/*.csv")
                if len(csv_file_list) != 0:
                    csv_file = csv_file_list[0]
                else:
                    print(f"This folder {data} has been skipped, if it contains important data, you need to check if a csv file is present within.")
                    continue
              
                csv_graph_save_root_path = os.path.join(data,"csv_images_files")
                if not os.path.isdir(csv_graph_save_root_path):
                    os.mkdir(csv_graph_save_root_path)
        
                self.graph_images(csv_file,csv_graph_save_root_path)

                video_file = glob(data+"/**/chest_cam_video.mp4")
                if len(video_file) == 0:
                    raise Exception("We can't find the video chest_cam_video.mp4")
                
                video_path = os.path.join(data,"video")
                if not os.path.isdir(video_path):
                    os.mkdir(video_path)
                
                new_video_file = os.path.join(video_path,"video.mp4")
                shutil.copyfile(video_file[0],new_video_file)

                images_path = os.path.join(data,"images")
                if not os.path.isdir(images_path):
                    os.mkdir(images_path)

                self.generate_images(video_file[0],images_path)
