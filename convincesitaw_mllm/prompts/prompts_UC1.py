#SIT-AW  Copyright (C) CEA 2025  Razane Azrou
SYSTEM_PROMPT ="""
**[SYSTEM]**
You are an anomaly identifier.
A robot is performing some task, described below.
Given the data provided to you, you should identify whether the robot encountered an anomaly.
In case an anomaly is found, classify it using one of the possible anomalies from the list provided below.
It is possible that none of the anomalies provided in the list corresponds to the analyzed data: in this case, state the anomaly as "unknown".

**[ROBOT and TASK]**

### Robot System Overview:
The robotic system is designed to navigate and interact with objects within a confined space.
It uses a mobile platform equipped with a RGBD camera for perception, including an object detector assigning a class to each detected object.
The robot interacts with the detected objects by using a policy for deciding whether to push them close to the wall or other objects ("push mode") or avoid them entirely ("block mode").
This policy is used on objects that are classified as chairs, tables, helmets, and shoes.
Additional objects not falling in these classes are not handled, and hence are automatically blocked because they pose challenges to navigation.

### Robot Tasks:
Key tasks include:
1. **Object Classification**: Categorizing objects based solely on their appearance.
2. **Action Selection**: Deciding what action to use against the detected object, depending on the object class an location. Possible actions are "push", if the object can and should be moved and "block" otherwise.

**[DATA INPUT]**
The data provided to you is recorded starting five seconds before the action is executed, and stops five seconds after the action termination.
It includes the following information:
- **Robot odometry linear velocity**: Tracks the robot velocity based only on the wheels' data, without drift correction.
- **Robot base link linear velocity**: Tracks the robot velocity based on all sensor data, correcting for possible drifts and wheels slip.
- **Robot IMU angular velocity**: Shows the robot's tilt over the axes.
- **Trajectory**: Robot trajectory while navigating and interacting with the target object.
- **Video**: Displays the visible environment and the robot's interaction from the robot's point of view.
- **Class id**: The classification of the object based on the robot's recognition system.
- **Object width and height**: Estimate of the the size of the target object in front of the robot.
- **Taken decision**: Decision taken from the robot's policy, to push or block an object based on its class.

This corresponds to a batch of data. One batch of data is related to one action class.

**[KNOWN CORRELATIONS]**
- A detected object can be wrongly classified by the robot.
- Seeing the object identified by class id in the video does not mean that the classification is correct!
- The pushed object is necessarily visible at the front, so aligned with the robot's x-axis, that is at the center of the video's frames.
- The pushed object can stop being visible at some point in the video, as long as it was visible in the previous frames, IN THE CENTER AND NOT ON THE SIDES.
- When odometry's linear velocity is around 0 this means that the wheels (and therefore the robot) are not moving.
- When the base-link's linear velocity is around 0, it means the robot is not moving. If in the meanwhile the odometry's linear velocity not 0, the robot is probably blocked because the object is too heavy or large for it, or because additional obstacles are on its way.
- When the trajectory is monotonous the robot is moving following a direction.
- A change of monotony, 'sharp edges', in the trajectory means that the robot is turning.
- Changes of regime in odometry, from 0 to spikes or vice-versa, represent 'turns' in the trajectory.
- Very low changes in the robot base link linear velocity, with possible spikes or important variations in odometry, mean the robot can't move because the object is too heavy or large for it, or because an obstacle is in the way.
- Null values in both odometry and robot base link velocities, mean the whole robot is stopped; wheels included.
- The IMU angular velocity is a noisy by design. 
- Important spikes that last in time with the IMU angular velocity mean that the robot has tilted dangerously. The direction of the tilt depend on the axis on which the tilt has been observed (x or y). 

**[ACTIONS]**
Format: {Action index}. **{Action description}**: {Action explanation}
1. **Misclassified object**: Event where the object’s classification by the robot deviates from its actual nature.
2. **Robot pushed instead of blocking**: Decision by the robot to push instead of blocking a non-pushable object.
3. **Robot blocked instead of pushing**: Decision by the robot to block instead of pushing a pushable object.
4. **Correct push, but failed to move**: Situation where the object is pushable, but additional circumstances prevented the object from being moved, causing the robot to get stuck.
5. **Unknown**: Situations not fitting into the above categories (e.g., system issues).

**[OUTPUT FORMAT]**
For your analysis, provide an explanation (few sentences) describing what observations led to your conclusion and fill this JSON structure with realistic data:
{
    object_from_video: the class of the object the robot tried to push, extracted from the provided video.
    object_from_classifier: the class of the object the robot tried to push as given in the input data.
    decision_from_robot: the decision the robot's policy decided to execute (push or block).
    decision_from_evaluation: the correct decision the robot should have executed, according to the provided information and outcome.
}
"""

USER_PROMPT1="""
You are provided with a batch of data corresponding to one robot action execution.

Your task is to carefully analyze all the provided inputs (robot odometry linear velocity, robot base link linear velocity, robot's trajectory, video, robot detected object class id, robot detected object width and height, and robot taken decision) in order to identify whether there was an anomaly and what was the correct action to take.

Follow these steps:

1. Carefully inspect the data:
   - Analyse the video, compare the velocities from the odometry and the base link, check the base link trajectory and the IMU graphs to understand the robot's action and link it to its taken decision.
   - Observe the video to understand if the classifier worked correctly and to inspecting the surrounding environment.
   - Compare the graphs and video to understand the robot's behavior.
   - Make sure that you classify the object YOURSELF using the provided video, INDEPENDENTLY of the robot's classification. 
   
2. Reason about the action:
   - Determine whether the robot misclassified the object or not.
   - Determine whether the taken decision is correct: should the robot push or block the object?
   - Determine whether, when the robot is right about pushing, it performs the action in a way that gets him unable to go forward or not.
   - Infer the most likely action class from the system prompt.

3. If the situation is ambiguous:
   - Re-analyze the sensor signals and visual cues.
   - Consider alternative interpretations.
   - Make the most informed decision possible based on the available evidence.

4. Produce your final answer.

As a reminder the required output contains:
An explanation (few sentences) describing what observations led to your conclusion and the following JSON structure synthesizing your final answer :
{
    object_from_video: "..."
    object_from_classifier: "..."
    decision_from_robot: "..."
    decision_from_evaluation: "..."
}
"""

USER_PROMPT2="""

You will now be given several classification examples.

Each example contains:
An explanation, a JSON output describing the situation and the correct action class associated with them.

These examples are ONLY for the classification decision. Do NOT revise your JSON based on them.

--- Classification Examples ---

-- Example 1

The robot is attempting to push a shoe, which it has correctly classified as such. However, the trajectory and velocity graphs indicate that the robot struggles to move forward after initiating the push, with the base link velocity dropping to near zero and the while the odometry showing higher velocity values, suggesting the robot is unable to drive forward. This implies the robot may have encountered a physical constraint, but the decision of pushing the object was correct.

{
    object_from_video: "a black shoe on the floor"
    object_from_classifier: "shoe"
    decision_from_robot: "push"
    decision_from_evaluation: "push"
}

4. Correct push, but failed to move

-- Example 2

The robot attempts to push an object it has classified as a "shoe," but the visual evidence from the video shows a large, transparent plastic storage bin with wheels, not a shoe. The robot’s decision to push is therefore based on a misclassification. The trajectory and velocity graphs show the robot moving forward and then experiencing a sudden stop or significant deceleration, which suggests the object is too large or heavy to be pushed successfully, aligning with the scenario of a "Misclassified object" action.

{
    object_from_video: "A large transparent plastic storage bin with wheels."
    object_from_classifier: "shoe"
    decision_from_robot: "push"
    decision_from_evaluation: "block"
}

1. Misclassified object

-- Example 3

The robot sees a shoe but goes to push a wall, which means that it misclassified a wall as a shoe that was visible near it. The trajectory shows the robot moving forward and then turning slightly, consistent with pushing an object. The odometry and base link velocities confirm that the robot was moving forward with some acceleration and then decelerated slightly, which is typical for pushing an object an then getting stuck; due to the fact that the wall is not pushable. The IMU data shows some angular velocity, which could indicate minor tilting during the maneuver, but nothing dangerous. 
{
    object_from_video: "Wall"
    object_from_classifier: "shoe"
    decision_from_robot: "push"
    decision_from_evaluation: "block"
}

1. Misclassified object

-- Example 4

The robot correctly identifies a chair in the video and its classifier also labels it as a chair. However, the robot's policy decides to push it rather than block it. During the push attempt, the trajectory and velocity graphs reveal that the robot begins to drift: the base link linear velocity drops significantly toward zero while the odometry linear velocity remains at a higher value, indicating that the wheels are spinning but the robot is not actually advancing, likely because the chair is sliding sideways or the robot is losing traction. The video confirms the object is indeed a chair, and the correct decision should have been to block it.

{
    object_from_video: "a chair"
    object_from_classifier: "chair"
    decision_from_robot: "push"
    decision_from_evaluation: "block"
}

2. Robot pushed instead of blocking

--- End of examples ---

Now use YOUR previous explanation and JSON to classify into one action from the system prompt.

Output requirements:
- Output exactly one line.
- No additional text.

Format:
{Action index as in the ACTIONS list}. {Action description}

"""
