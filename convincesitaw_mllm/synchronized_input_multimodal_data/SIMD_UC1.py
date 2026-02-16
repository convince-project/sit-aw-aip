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

#For this I consider there is a rosbag encoded in mcap
#need to be adapted if want to use a direct connection with ros
#don't forget to source your workspace if needed
class UC1(SIMD):

    def __init__(self):
        
        super().__init__()


    def read_extract_from_bag(self,data_path,reader,topic_types):

        odom_linear_vel = []
        current_pose_diff_linear_vel = []
        imu_ang_vel_y = []
        trajectory_from_base_link = []
        dv = []
        time_odom = []
        time_imu = []
        time_base_l_vel = []
        valid_images = []
        bridge = CvBridge()

        i = 0
        while reader.has_next():
            topic,msg_data,_ = reader.read_next()

            if topic == "/odom":
                
                msg_type = get_message(topic_types[topic])
                msg = deserialize_message(msg_data,msg_type)
                t_ns = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9

                vx = msg.twist.twist.linear.x
                time_odom.append(t_ns)
                odom_linear_vel.append(vx)

            if topic == "/push_rl/selected_action":
                
                msg_type = get_message(topic_types[topic])
                msg = deserialize_message(msg_data,msg_type)
                obj_class = msg.detection.class_id
                obj_estimated_h = msg.detection.height
                obj_estimated_w = msg.detection.width
                taken_decision = msg.taken_action

            if topic == "/imu":
                
                msg_type = get_message(topic_types[topic])
                msg = deserialize_message(msg_data,msg_type)
                imu_time_ns = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9

                time_imu.append(imu_time_ns)

                ang_vel_x = msg.angular_velocity.x
                ang_vel_y = msg.angular_velocity.y
            
                imu_ang_vel_y.append(np.array([ang_vel_x,ang_vel_y]))

            if topic == "/realsense/camera/color/image_raw":
                
                msg_type = get_message(topic_types[topic])
                msg = deserialize_message(msg_data,msg_type)

                cv_img = bridge.imgmsg_to_cv2(msg,desired_encoding="passthrough")
                cv2.imwrite(f"{data_path}/images/saved_image_{i}.jpg", cv_img)
                valid_images.append(f"{data_path}/images/saved_image_{i}.jpg")
                i+=1

            if topic == "/base_link/current_pose":
                msg_type = get_message(topic_types[topic])
                msg = deserialize_message(msg_data,msg_type)
                base_time = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
                
                cc_x = msg.pose.position.x
                cc_y = msg.pose.position.y

                dv.append(cc_x)
                if len(dv) == 2:
                    time_base_l_vel.append(base_time)
                    vx = dv[1] - dv[0]
                    current_pose_diff_linear_vel.append(vx)
                    dv = []

                trajectory_from_base_link.append(np.array([cc_x,cc_y]))

        fig1,trajectory = plt.subplots(1,figsize=(15,15))
        fig2,odom_in_time = plt.subplots(1,figsize=(15,15))
        fig3,base_current_pose = plt.subplots(1,figsize=(15,15))
        fig4,imu_y_axis_angular_velocity = plt.subplots(2,1,sharex=True,sharey=True,figsize=(15,15))

        time_odom = np.array(time_odom) - time_odom[0]
        imu_time = np.array(time_imu) - time_imu[0]
        time_base_l_vel = np.array(time_base_l_vel) - time_base_l_vel[0]

        odom_linear_vel = np.array(odom_linear_vel)
        imu_ang_vel_y = np.array(imu_ang_vel_y)
        current_pose_diff_linear_vel = np.array(current_pose_diff_linear_vel)
        trajectory_from_base_link = np.array(trajectory_from_base_link) 
        distance= 0
        for i in range(trajectory_from_base_link.shape[0]):
            distance += math.sqrt(((trajectory_from_base_link[i,0]-trajectory_from_base_link[i-1,0])**2+(trajectory_from_base_link[i,1]-trajectory_from_base_link[i-1,1])**2))

        cur_pose_lin_vel = []
        for cur_l_pos,time_c_vel in zip(*(current_pose_diff_linear_vel,time_base_l_vel)):
            cur_l_pos = cur_l_pos/(time_c_vel+10e-15)
            cur_pose_lin_vel.append(cur_l_pos)

        cur_pose_lin_vel = np.array(cur_pose_lin_vel)

        trajectory.plot(trajectory_from_base_link[:,0],trajectory_from_base_link[:,1])
        trajectory.scatter(trajectory_from_base_link[0,0], trajectory_from_base_link[0,1], color='blue', s=60, label='Start')
        trajectory.scatter(trajectory_from_base_link[-1,0], trajectory_from_base_link[-1,1], color='red', s=60, label='End')
        trajectory.set_xlabel('x', fontsize=18)
        trajectory.set_ylabel('y', fontsize=18)
        trajectory.legend()
        fig1.suptitle("Trajectory", fontsize=18)

        odom_in_time.plot(time_odom,odom_linear_vel)
        odom_in_time.set_ylabel("odometry_velocity_x", fontsize=18)
        odom_in_time.set_xlabel("time(s)", fontsize=18)
        fig2.suptitle("Linear velocity given by odometry for each planar axis", fontsize=18)

        base_current_pose.plot(time_base_l_vel,cur_pose_lin_vel)
        base_current_pose.set_ylabel("base_link_current_linear_velocity_x", fontsize=18)
        base_current_pose.set_xlabel("time(s)", fontsize=18)
        fig3.suptitle("Linear velocity given by base link current pose for each planar axis", fontsize=18)

        imu_y_axis_angular_velocity[0].plot(imu_time,imu_ang_vel_y[:,0])
        imu_y_axis_angular_velocity[1].plot(imu_time,imu_ang_vel_y[:,1])
        imu_y_axis_angular_velocity[0].set_ylabel('Angular velocity - x axis', fontsize=18)
        imu_y_axis_angular_velocity[1].set_ylabel('Angular velocity - y axis', fontsize=18)
        imu_y_axis_angular_velocity[1].set_xlabel('time(s)', fontsize=18)
        fig4.suptitle("Angular velocity from IMU",fontsize=18)

        fig1.savefig(f"{data_path}/csv_images_files/trajectory.png")
        fig2.savefig(f"{data_path}/csv_images_files/odom_vel.png")
        fig3.savefig(f"{data_path}/csv_images_files/base_current_vel.png")
        fig4.savefig(f"{data_path}/csv_images_files/angular_imu_vel.png")

        with open(f"{data_path}/text_files/class_action.txt","w") as file:
            file.write(f"class_id : {obj_class}\n")
            file.write(f"object_width : {obj_estimated_w}\n")
            file.write(f"object_height : {obj_estimated_h}\n")
            file.write(f"taken_decision : {taken_decision}\n")
            file.write(f"distance : {distance}\n")

        avg_total_time = (time_odom[-1]+time_base_l_vel[-1]+imu_time[-1])/3
        total_frame = len(valid_images)
        fps = total_frame//avg_total_time

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
    
    def main(self,root_path):

        data_folders = glob(root_path+"/*")
        for anomaly_folder in data_folders:

            ros_bag_file = glob(anomaly_folder+f"/*.mcap")
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
            if not os.path.isdir(anomaly_folder+"/text_files"):
                os.mkdir(anomaly_folder+"/text_files")
            if not os.path.isdir(anomaly_folder+"/video"):
                os.mkdir(anomaly_folder+"/video") 

            self.read_extract_from_bag(anomaly_folder,reader,topic_types)
