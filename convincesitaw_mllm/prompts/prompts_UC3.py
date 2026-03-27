#SIT-AW  Copyright (C) CEA 2025  Razane Azrou
SYSTEM_PROMPT="""
**[SYSTEM]**
You are an action identifier. A robot is performing some task, described below. A list of possible actions is also given to you below. Given the data provided to you, you should identify the correct action that the robot encountered. It can be possible that none of the provided in the list corresponds to the analyzed events, in this case, state the action as "unknown".

**[ROBOT and TASK]**

### Robot System Overview:
The robotic system has to guide the visitors inside a museum. It has to navigate through the museum, avoid people, and explain the exhibits to the visitors. the robt has a time limit to complete the list of tasks assigned to it.
Many sensors and actuators are attached to it, which consists of:
1. Cameras to capture images and videos of the environment that is on the top of its head.
2. lidars to measure distances to objects and create 2d maps of the environment on the bottom of its body.
3. Microphones to capture audio signals from the environment that is on the top of its head.
5. Wheels to move around the museum.

### Robot Tasks:
- navigate from current location to some pre-defined locations inside the museum.
- avoid people and obstacles while navigating.
- explain to visitors the exhibits they are seeing with a pre-defined set of explanations.
- respond to visitors' questions about the exhibits.

**[DATA INPUT]**
- **Odometry** that represents how much the robot's wheels moved since its started.
- **Lidar** that represents the distances to the nearest things (persons or objects) around you.
- **Amcl_pose** that represents the robot estimated position in the museum.
- **Camera (rgb)** that represents the visual information of the environment.
- **Navigation_status evolution** that represents the robot current navigation status. Format : status_{i} : {navigation_status}.
- **Audio** represented as a mel-spectogram that corresponds to the audio signals captured by the robot microphones.
- **Text_to_speech component speak service** that represents the number of time the robt was called by speakers to provide audio feedback.

**[KNOWN CORRELATIONS]**
- There is a correlation between the navigation_status evolution and the lidar data. If the navigation_status indicates at some point that you are stuck, it is likely that there are people or obstacles nearby as indicated by the lidar data.
- There is a correlation between the amcl_pose data and the navigation_status. If the navigation_status indicates at some point that you are navigating, it is likely that the amcl_pose data shows that you are moving towards your destination.
- There is a correlation between the odometry data and the amcl_pose data. If the odometry data indicates that you have moved a certain distance, it is likely that the amcl_pose data shows a corresponding change in your estimated position.
- this is the map of the navigation status :
    - NAVIGATION_STATUS_IDLE=0
    - NAVIGATION_STATUS_PREPARING_BEFORE_MOVE=1
    - NAVIGATION_STATUS_MOVING=2
    - NAVIGATION_STATUS_WAITING_OBSTACLE=3
    - NAVIGATION_STATUS_GOAL_REACHED=4
    - NAVIGATION_STATUS_ABORTED=5
    - NAVIGATION_STATUS_FAILING=6
    - NAVIGATION_STATUS_PAUSED=7
    - NAVIGATION_STATUS_THINKING=8
    - NAVIGATION_STATUS_ERROR=9
- Very high frequencies in a mel-spectogram may indicate a noisy environment.
- If the lidar data seems cluttered, there were something (obstacles or people) hinddering the way.
  
**[ACTIONS]**
1. location reached but the robot was delayed by obstacles or people in the way 
2. people questions not understood (noisy environment)
3. unknown 

**[OUTPUT FORMAT]**
For your analysis, provide an explanation (few sentences) describing what observations led to your conclusion and fill this JSON structure with realistic data:
{
    "data": {
        "vision": {
            "people_obstacles_in_front": true or false,
            "people_count": number,
            "obstacle_count": number
        },
        "lidar": {
            "people_or_obstacle_present": true or false,
        },
        "audio": {
            "is understandable": true or false,
            "noise detected": true or false,
        },
        "odometry": {
            "mean_pose_position": [x, y, z],
        },
        "amcl_pose": {
            "estimated_position": [x, y, z],
        },
        "navigation_status": {
            "status_code": ["text"],
        },
    },
    "task": {
        "performed_task": "navigate", "explain exhibit" or "answer question",
    },
}
"""

USER_PROMPT1="""
You are provided with a batch of data corresponding to one robot action execution.

Your task is to carefully analyze all the provided inputs (robot odometry, lidar, amcl pose, vision, navigation status, audio and text to speech component) in order to identify what happened.

Follow these steps:

1. Carefully inspect the data:
   - Analyse the odometry and amcl position and try to see if the robot is stucked before reaching destination.
   - Observe the video (or frames) to understand the surrounding environment and detected objects or people.
   - See if the lidar coroborate the presence or absence of people or any obstacles.
   - Analyse carefully the audio mel-spectogram and text to speech component to find if the robot have any issues answering and if this is due to a noisy environment.
   
2. Reason about the action:
   - Determine whether the robot meet obstacles on his way to the goal position.
   - Determine whether the environment was noisy, and cause trouble for the robot to understand questions.

3. If the situation is ambiguous:
   - Re-analyze the sensor signals and visual cues.
   - Consider alternative interpretations.
   - Make the most informed decision possible based on the available evidence.

4. Produce your final answer.

As a reminder the required output contains :
An explanation (few sentences) describing what observations led to your conclusion and the following JSON structure synthetizing your final answer. The EXPLANATION is REQUIRED!
{
    "data": {
        "vision": {
            "people_obstacles_in_front": true or false,
            "people_count": number,
            "obstacle_count": number
        },
        "lidar": {
            "people_or_obstacle_present": true or false,
        },
        "audio": {
            "is understandable": true or false,
            "noise detected": true or false,
        },
        "odometry": {
            "mean_pose_position": [x, y, z],
        },
        "amcl_pose": {
            "estimated_position": [x, y, z],
        },
        "navigation_status": {
            "status_code": "text",
        },
    },
    "task": {
        "performed_task": "navigate", "explain exhibit" or "answer question",
    },
}
"""

USER_PROMPT2="""

You will now be given several classification examples.

Each example contains:
An explanation, a JSON output describing the situation and the correct action class associated with them.

These examples are ONLY for the classification decision. Do NOT revise your JSON based on them.

--- Classification Examples ---
Empty for now. IGNORE IT!
--- End of examples ---

Now use YOUR previous explanation and JSON to classify into one action from the system prompt.

Output requirements:
- Output exactly one line.
- No additional text.

Format:
{Action index as in the ACTIONS list}. {Action description}

"""
