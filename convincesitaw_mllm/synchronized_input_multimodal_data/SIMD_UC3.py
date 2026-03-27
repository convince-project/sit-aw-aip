#SIT-AW  Copyright (C) CEA 2025  Razane Azrou
from .SIMD_abstract import SIMD
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
import matplotlib
matplotlib.use("Agg")  # non-GUI backend
import matplotlib.pyplot as plt
import numpy as np
from cv_bridge import CvBridge
import cv2
import math
from glob import glob
import os
import librosa

#I subsampled lidar, odom and images because it is too high and the computer crashes
class UC3(SIMD):

    def __init__(self):
        
        super().__init__()


    def read_extract_from_bag(self,data_path,reader,topic_types):
        
        odometry_positions = []
        amcl_positions = []
        lidar_lst = []
        valid_images = []
        is_speacking = []
        t_odom = []
        t_amcl = []
        bridge = CvBridge()
        st_evolution = []

        i = 0
        skip = 0
        while reader.has_next():
            topic,msg_data,_ = reader.read_next()

            if topic == "/odometry" and skip%10==0 :
    
                msg_type = get_message(topic_types[topic])
                msg = deserialize_message(msg_data,msg_type)
                t_ns = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9

                x = msg.pose.pose.position.x
                y = msg.pose.pose.position.y
            
                t_odom.append(t_ns)
                odometry_positions.append(np.array([x,y]))

            if topic == "/laser_local" and skip%10==0 :

                msg_type = get_message(topic_types[topic])
                msg = deserialize_message(msg_data,msg_type)

                angle_min = msg.angle_min
                angle_max = msg.angle_max
                angle_increment = msg.angle_increment
                ranges = np.array(msg.ranges)

                ranges[ranges==np.inf] = None
                ranges[ranges == 0] = None

                angles_rad = np.arange(angle_min, angle_max, angle_increment)
                
                x_l = ranges*np.cos(angles_rad)
                y_l = ranges*np.sin(angles_rad)

                lidar_lst.append(np.array([x_l,y_l]))
            
            skip += 1 

            if topic == "/amcl_pose":
                
                msg_type = get_message(topic_types[topic])
                msg = deserialize_message(msg_data,msg_type)

                t = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
                t_amcl.append(t)

                x = msg.pose.pose.position.x
                y = msg.pose.pose.position.y

                amcl_positions.append(np.array([x,y]))

            if topic == "/TextToSpeechComponent/is_speaking":
                
                msg_type = get_message(topic_types[topic])
                msg = deserialize_message(msg_data,msg_type)

                data = msg.data
                is_speacking.append(data)

            if topic == "/image_rgb" :
                
                msg_type = get_message(topic_types[topic])
                msg = deserialize_message(msg_data,msg_type)

                cv_img = bridge.imgmsg_to_cv2(msg,desired_encoding="passthrough")
                cv2.imwrite(f"{data_path}/images/saved_image_{i}.png", cv_img)
                valid_images.append(f"{data_path}/images/saved_image_{i}.png")
                i+= 1

            if topic == "/NavigationComponent/GoToPoi/_action/status":
		
                msg_type = get_message(topic_types[topic])
                msg = deserialize_message(msg_data,msg_type)

                status = msg.status_list[0].status
                st_evolution.append(status)

        fig1,odom = plt.subplots(2,1,figsize=(15,15))
        fig2,amcl = plt.subplots(2,1,figsize=(15,15))
        fig3,lidar = plt.subplots(1,figsize=(15,15))
        fig4,speaking = plt.subplots(1,figsize=(15,15))

        # ################### Odometry ############################
        time_odom = np.array(t_odom) - t_odom[0]
        odometry_positions = np.array(odometry_positions)

        odom[0].plot(time_odom,odometry_positions[:,0])
        odom[1].plot(time_odom,odometry_positions[:,1])
        
        odom[0].set_ylabel('odometry x position', fontsize=18)
        odom[1].set_ylabel('odometry y position', fontsize=18)
    
        odom[1].set_xlabel('time(s)', fontsize=18)

        fig1.suptitle("Odometry position",fontsize=18)
        fig1.savefig(f"{data_path}/csv_images_files/odom.png")

        # ##########################################################
        # ###################### lidar #############################

        freq_subsample = round(len(lidar_lst)/len(odometry_positions))
        subsampled_lidar = []
        for i in range(0,len(lidar_lst),freq_subsample):
            subsampled_lidar.append(lidar_lst[i])
        if len(subsampled_lidar) > len(odometry_positions):
            subsampled_lidar = subsampled_lidar[:len(odometry_positions)]
        else:
            odometry_positions = odometry_positions[:len(subsampled_lidar)]

        subsampled_lidar = np.array(subsampled_lidar)
        odometry_positions = np.array(odometry_positions)

        x_r = odometry_positions[:,0][:,None] + subsampled_lidar[:,0,:]
        y_r = odometry_positions[:,1][:,None] + subsampled_lidar[:,1,:]

        lidar.plot(odometry_positions[0,0],odometry_positions[0,1],'oy',label='start')
        lidar.plot(odometry_positions[-1,0],odometry_positions[-1,1], 'og',label='end')
        for i in range(x_r.shape[0]):
            lidar.plot(odometry_positions[:,0],odometry_positions[:,1],'r')
            lidar.scatter(x_r[i, :], y_r[i, :],c="#1f77b4")

        lidar.legend()
        fig3.suptitle("lidar",fontsize=18)
        fig3.savefig(f"{data_path}/csv_images_files/lidar.png")

        # ###########################################################
        # ################### amcl_pose ############################
        time_amcl = np.array(t_amcl) - t_amcl[0]
        amcl_positions = np.array(amcl_positions)

        amcl[0].plot(time_amcl,amcl_positions[:,0])
        amcl[1].plot(time_amcl,amcl_positions[:,1])

        amcl[0].set_ylabel('amcl x position', fontsize=18)
        amcl[1].set_ylabel('amcl y position', fontsize=18)

        amcl[1].set_xlabel('time(s)', fontsize=18)

        fig2.suptitle("amcl_positions",fontsize=18)
        fig2.savefig(f"{data_path}/csv_images_files/amcl.png")
        #######################################################

        ################### is_speaking ######################
        speaking.plot(is_speacking)
        fig4.suptitle("state of the robot speaking",fontsize=18)
        fig4.savefig(f"{data_path}/csv_images_files/is_speaking.png")

        ######################################################
        ################### video ##########################
        avg_total_time = (time_odom[-1]+time_amcl[-1])/2
        total_frame = len(valid_images)
        fps = total_frame//avg_total_time
        print(f"fps:{fps}")

        video_path = f"{data_path}/video/video.mp4"

        if len(valid_images) !=0 :
            first_image = cv2.imread(valid_images[0])
            
            h, w, _ = first_image.shape
            codec = cv2.VideoWriter_fourcc(*'mp4v')
            vid_writer = cv2.VideoWriter(video_path, codec, fps, (w, h))
            for img in valid_images:
                loaded_img = cv2.imread(img) 
                vid_writer.write(loaded_img)
                    
            vid_writer.release()

        ######################################################
        ################### navigation status ##########################
        with open(f"{data_path}/text_files/navigation_status_evolution.txt","w") as file:
            for s in range(len(st_evolution)):
                file.write(f"status_{s} : {st_evolution[s]}\n")
        
    def convert_audio_to_melspec(self,audio_file,data_path):

        fig, ax = plt.subplots()
        array,sr = librosa.load(audio_file) #return tuple : array, sampling_rate is in Hz
        S = librosa.feature.melspectrogram(y=array,sr=sr)
        S_dB = librosa.power_to_db(S,ref=np.max)
        img = librosa.display.specshow(S_dB, x_axis='time', y_axis='mel', sr=sr, ax=ax)
        fig.colorbar(img, ax=ax, format='%+2.0f dB')
        ax.set(title='Mel-frequency spectrogram')
        file_name = audio_file.split('/')[-1].split('.')[0]
        fig.savefig(f"{data_path}/audio_images_files/mel_spectorgam_{file_name}.png")
        plt.close()
         
    def main(self,root_path):

        data_folders = glob(root_path+"/*")
        for anomaly_folder in data_folders:

            ros_bag_file = glob(anomaly_folder+"/*.mcap")
            if len(ros_bag_file)==0:
                print(f"This {anomaly_folder} has been skipped, if it contains important data, you need to check if a mcap file is present within.")
                continue
            else:
                ros_bag_file = ros_bag_file[0]

            reader = rosbag2_py.SequentialReader()

            storage_opts = rosbag2_py.StorageOptions(uri=ros_bag_file, storage_id="mcap")
            converter_opts = rosbag2_py.ConverterOptions("","")

            reader.open(storage_opts,converter_opts)
            topic_types = {topic_info.name: topic_info.type for topic_info in reader.get_all_topics_and_types()}

            if not os.path.isdir(anomaly_folder+"/csv_images_files"):
                os.mkdir(anomaly_folder+"/csv_images_files")
            if not os.path.isdir(anomaly_folder+"/images"):
                os.mkdir(anomaly_folder+"/images")
            if not os.path.isdir(anomaly_folder+"/video"):
                os.mkdir(anomaly_folder+"/video") 
            if not os.path.isdir(anomaly_folder+"/text_files"):
                os.mkdir(anomaly_folder+"/text_files")

            self.read_extract_from_bag(anomaly_folder,reader,topic_types)

            audio_folder = glob(anomaly_folder+"/audio/*.wav")
            if len(audio_folder) == 0:
                raise Exception(f"No audio file detected at {anomaly_folder}/audio")

            if not os.path.isdir(anomaly_folder+"/audio_images_files"):
                os.mkdir(anomaly_folder+"/audio_images_files")
            
            for audio_file in audio_folder:
                self.convert_audio_to_melspec(audio_file,anomaly_folder)
