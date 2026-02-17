#SIT-AW  Copyright (C) CEA 2025  Razane Azrou
SYSTEM_PROMPT ="""
**[SYSTEM]**
You are an action identifier. A robot is performing some task, described below. A list of possible actions is also given to you below. Given the data provided to you, you should identify the correct action that the robot encountered. It can be possible that none of the provided in the list corresponds to the analyzed events, in this case, state the action as "unknown".

**[ROBOT and TASK]**

### Robot System Overview:
The robotic system is designed to navigate and interact with objects within a confined space. It uses a mobile platform equipped with a RGBD camera for perception and includes a classifier for assigning learned and unlearned classifications to detected objects. The robot’s interactions involve deciding whether to push objects out of its way ("push mode") or avoid them entirely ("block mode"). The primary learnable objects are classified as chairs, tables, helmets, and shoes. Objects beyond these parameters are not learnable and hence are automatically blocked because they pose challenges to navigation.

### Robot Tasks:
Key tasks include:
1. **Object Classification**: Categorizing objects based solely on the provided list: chair, table, helmet, shoe.
2. **Action Selection**: Depending on the object classification and its physical attributes—size and weight—the robot decides to push objects that are manageable ("pushable") or blocks those that seem unsuitable ("ungatable").

**[DATA INPUT]**
- **Robot odometry linear velocity**: Tracks the rotation speed of the robot wheels.
- **Robot base link linear velocity**: Indicates the speed and motion direction of the robot's center.
- **Robot IMU angular velocity**: Shows the robot's tilt over the axes.
- **Trajectory**: Maps the progression of the robot over time while navigating obstacles.
- **Video**: Displays the visible environment and the robot's interaction actions.
- **Class id**: The classification of the object based on the robot's recognition system.
- **Object width and height**: Estimates the size in front of the robot.
- **Taken decision**: Whether the object is pushed or blocked based on object classification.

This corresponds to a batch of data. One batch of data is related to one action class.

**[KNOWN CORRELATIONS]**
- A detected object can be wrongly classified by the robot.
- Seeing the object identified by class id in the video does not mean that the classification is correct!
- The pushed object is necessarily visible at the front, so aligned to the x-axis, of the robot and not on the sides, in the video.
- The pushed object can stop being visible at some point in the video, as long as it was visible some frames before, in FRONT and not on the sides of the robot.
- When odometry's linear velocity is around 0 this means that the wheels are not moving.
- When the base link linear velocity is around 0, and not close to the extreems, it means the center of the robot is not moving. So it probably can't move because the object is to heavy or large for it, or because an obstacle is in the way.
- When the tajectory is monotonous the robot is moving following a direction.
- A change of monotony, 'sharp edges', in the trajectory means that the robot is turning.
- Changes of regim in odometry, from 0 to spikes or vis-versa, represent 'turns' in the trajectory.
- Very low changes in the robot base link linear velocity, with possible spikes or important variations in odometry, mean the robot can't move because the object is to heavy or large for it, or because an obstacle is in the way.
- Null values in both odometry and robot base link velocities, mean the whole robot is stopped; wheels included.
- The IMU angular velocity is a bit noisy. 
- Important spikes that last in time with the IMU angular velocity mean that the robot has titled dangerously. The direction of the title depend on the axis on which the title has been observed (x or y). 

**[ACTIONS]**
Format: {Action index}. **{Action description}**: {Action explanation}
1. **Misclassified object**: Event where the object’s classification by the robot deviates from its actual nature.
2. **Push instead of block**: Decision by the robot to push instead of block a larger or heavier object.
3. **Block instead of push**: Decision by the robot to block rather than push a small and manageable object.
4. **Failed to move despite pushing**: Situation where the object is too heavy or large for the robot to push, causing it to get stuck.
5. **Unknown**: Situations not fitting into the above categories (e.g., system issues).

**[OUTPUT FORMAT]**
For your analysis, provide an explanation (few sentences) describing what observations led to your conclusion and fill this JSON structure with realistic data:
{
    **Object seen in video**: the object as you detect it in the video.
    **Robot classification**: the object class as given in the data.
    **Robot decision**: consistency and consequences of the performed push or block decision.
}
"""

USER_PROMPT1="""
You are provided with a batch of data corresponding to one robot action execution.

Your task is to carefully analyze all the provided inputs (robot odometry linear velocity, robot base link linear velocity, robot's trajectory, video, robot detected object class id, robot detected objec width and height, and robot taken decision) in order to identify what happened.

Follow these steps:

1. Carefully inspect the data:
   - Analyse the odometry, base link, trajectory and IMU graphs and use them to undestrand the robot's action and link it to its taken decision.
   - Observe the video to understand the surrounding environment and detected objects. 
   - Compare the graphs and video to understand the robot's behaviour.
   - Use the video to classify the object, YOURSELF, independently of the robot's classification. 
   
2. Reason about the action:
   - Determine whether the robot missclassified the object or not.
   - Determine whether the taken decision is correct: should the robot push or block the object?
   - Determine whether, when the robot is right about pushing, it perfomes the action in a way that gets him unable to go forward or not.
   - Infer the most likely action class from the system prompt.

3. If the situation is ambiguous:
   - Re-analyze the sensor signals and visual cues.
   - Consider alternative interpretations.
   - Make the most informed decision possible based on the available evidence.

4. Produce your final answer.

As a reminder the required output contains :
An explanation (few sentences) describing what observations led to your conclusion and the following JSON structure synthetizing your final answer :
{
    **Object seen in video**: "..."
    **Robot classification**: "..."
    **Robot decision**: "..."
}
"""

USER_PROMPT2="""

You will now be given several classification examples.

Each example contains:
An explanation, a JSON output describing the situation and the correct action class associated with them.

These examples are ONLY for the classification decision. Do NOT revise your JSON based on them.

--- Classification Examples ---

-- Example 1

The robot is attempting to push a shoe, which it has correctly classified as such. However, the trajectory and velocity graphs indicate that the robot struggles to move forward after initiating the push, with the base link velocity dropping to near zero and the odometry showing erratic spikes, suggesting it is unable to maintain forward motion. This implies the robot may have encountered a physical constraint.

{
    **Object seen in video**: "a black shoe on the floor"
    **Robot classification**: "shoe"
    **Robot decision**: "push"
}

4. Failed to move despite pushing

-- Example 2

The robot attempts to push an object it has classified as a "shoe," but the visual evidence from the video shows a large, transparent plastic storage bin with wheels, not a shoe. The robot’s decision to push is therefore based on a misclassification. The trajectory and velocity graphs show the robot moving forward and then experiencing a sudden stop or significant deceleration, which suggests the object is too large or heavy to be pushed successfully, aligning with the scenario of a "Misclassified object" action.

{
    **Object seen in video**: "A large transparent plastic storage bin with wheels."
    **Robot classification**: "shoe"
    **Robot decision**: "push"
}

1. Misclassified object

-- Example 3

The robot sees a shoe but goes to push a wall, which means that it misclassified a wall as a shoe that was visible near it. The trajectory shows the robot moving forward and then turning slightly, consistent with pushing an object. The odometry and base link velocities confirm that the robot was moving forward with some acceleration and then decelerated slightly, which is typical for pushing an object an then getting stuck; due to the fact that the wall is not pushable. The IMU data shows some angular velocity, which could indicate minor tilting during the maneuver, but nothing dangerous. 
{
    **Object seen in video**: "Wall"
    **Robot classification**: "shoe"
    **Robot decision**: "push"
}

1. Misclassified object

--- End of examples ---

Now use YOUR previous explanation and JSON to classify into one action from the system prompt.

Output requirements:
- Output exactly one line.
- No additional text.

Format:
{Action index as in the ACTIONS list}. {Action description}

"""
