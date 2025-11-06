This project allows to use a VLM for anomaly identification.
The deployment of the VLM is explained in [here](#vlm-deployement).
And the way to communicate with the model [here](#inference-with-vlm), given [CONVINCE](https://convince-project.eu/) use cases. For now only UC1, vacuum cleaner, and UC2, assembly robot.
The last [section](#customize-communication) explains how to custom the communication.

The tests have been done only on LINUX. 

# Requirements : Install docker

## Linux (Ubuntu >= 22.04) - [Source](https://docs.docker.com/engine/install/ubuntu/) to also check other OSs

⚠ You need to have sudo rights

### Uninstall unofficial packages
```
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done
```
### Set up
```
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```
### Install packages
```
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
### Start docker services if disabled
```
sudo systemctl status docker
sudo systemctl start docker
```
### Running without sudo
```
sudo usermod -aG docker $USER
newgrp docker
```
### Verify installation
```
docker run hello-world
```

# VLM deployement

To deploy the VLM and use it, you will need a machine that contains more that 40 GB of Vram and more than 30 GB of cache memory (RAM).

You will have to install [docker](#requirements--install-docker) and  install Nvidia container toolkit by following these [instructions](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).

Once you selected the host machine for the model.

### Optional - Clone only the corresponding folder

#### Works with Git > 2.27 and the remote server need to support partial clone filtering 
```
git clone --filter=blob:none --no-checkout https://gitlab.lri.cea.fr/razane.azrou/convincesitaw-mllm.git
cd convincesitaw-mllm
git sparse-checkout init --cone
git sparse-checkout set /vLLM-hosting
git checkout
```

### Else clone the whole project and consider only the *vLLM-hosting* folder
```
git clone https://gitlab.lri.cea.fr/razane.azrou/convincesitaw-mllm.git
cd convincesitaw-mllm/vLLM-hosting
```

#### Then execute **bash** file 
```
deploy_model.sh
```
#### You may need to give execute permissions (on Linux)
```
sudo chmod +x deploy_model.sh
```
#### If your are not using bash you can directly build then run the docker compose in your terminal
```
docker compose build
docker compose up -d
```
#### The *.env* file allows you to change some parameters
- **MODEL** : The model to deploy - default Qwen2.5-VL
- **PORT** : Exposed and container port - default 23333
- **GPU_MEMORY_USAGE** : The portion (< 1) of GPU usage allowed to the model given GPU capacities -- default 0.85
- **DOWNLOAD_MODEL_CACHE_DIR** : Machine's directory to download cached model to - default "./.cache/huggingface"

⚠ **Changing the model may need different GPU memory usage or disk capacity to where to download the cached model. It is quite specific to the model, so you may need a more powerful machine**

# Inference with VLM 

## Clone project 
```
git clone https://gitlab.lri.cea.fr/razane.azrou/convincesitaw-mllm.git
```
⚠ **At this stage ignore vLLM-hosting folder**

### Build your project - Once
```
uv sync --frozen 
```
### Activate virtual env - everytime you enter the project
```
source .venv/bin/activate
```
### Import critics package
```
vcs import < critics.repos
```


### Format data - generate json (Once on a desired batch of data)

**This script will generate the [json_files](#variables-) that will be used by the model**

```
fData \
--use_case_id {id} \
--root_path {root_path}
```

#### Variables :
**use_case_id** : 1,2 or 3 given CONVINCE Use cases order

**root_path** : root_path to all anomalies data, the folders need to be structured this way given the use case :

##### UC1
```
-- root 
  -- Anomaly 1
    -- excel_files
      clif_sensors_data.xlsx
      imu_data_data.xlsx
      odometrie_data.xlsx
      wheel_lift_data.xlsx
    --images
      [all images files]
    -- json_files (optional)
  -- Anomaly 2 (same as 1)
  -- Anomaly 3 (same as 1)
  -- (repeat)
```
**The excel files columns and representation (elements in brackets represent numbers) - please refer for your data structure** :

*clif_sensors_data.xlsx* :
| (empty) | Data |
| ------- | ---- |
| {timestamp_0} | {value_0} |

*imu_data_data.xlsx* :
| (empty) | Orientation | Orientation covariance | Angular velocity | Angular velocity covariance | Linear Acceleration | Linear Acceleration covariance |
| ------- | ---- | ---- | ---- | ---- | ---- | ---- | 
| {timestamp_0} | {[list]} | {[list]} | {[list]} | {[list]} | {[list]} | {[list]} |

*odometrie_data.xlsx*
| (empty) | Pose position | Pose orientation | Pose covariance | Twist linear | Twist angular | Twist covariance |
| ------- | ---- | ---- | ---- | ---- | ---- | ---- | 
| {timestamp_0} | {[list]} | {[list]} | {[list]} | {[list]} | {[list]} | {[list]} |

*wheel_lift_data.xlsx*
| (empty) | Data |
| ------- | ---- |
| {timestamp_0} | {value_0} |

##### UC2
```
-- root 
  -- Anomaly 1
    -- block 1
      -- folder 1 (the name is not important)
        chest_cam_video.mp4
        proprioception.csv
      -- folder 2 (the name is not important)
        scan_image.png
      -- json_files (optional)
    -- block 2 (same as block1)
    -- block 3 (same as block1)
    -- (repeat)
  -- Anomaly 2 (same as Anomaly 1)
  -- (repeat)
```
**Csv file columns and representation (elements in brackets represent numbers) - please refer for your data structure**

| timestamp | name | position |
| ------- | ---- | ---- |
| {timestamp_0} | gripper_jaws | {value_0} | 

Other names in the *name* column can be present, but the **gripper_jaws** has to be.

**Example given [uc1](#uc1) previously presented data structre** :
```
fData \
--use_case_id 1 \
--root_path home/root/
```

### Send an identification request to the VLM server

```
identif \
--use_case_id {id} \
--anomaly_case_path {root_path_to_one_anomaly_case}
```
#### Variables :

There are three environment variables defined in the *.env* at the root. The **SERVER_IP** variable need to be changed to the IP of the distant machine where the model is hosted, else it will consider localhost and result in error.
The two other variables **MODEL** and **PORT** have to correspond with the ones defined when deploying the model. 

**use_case_id** : 1,2 or 3 given the use case you want to treat within CONVINCE use case.

**anomaly_case_path**: within the selected use case and the [formatted data](#format-data---generate-json-once-on-a-desired-batch-of-data), the root_path to the desired anomaly to treat, where a *json_files* folder is. 

**Example given [uc2](#uc2) previously presented data structre** :
```
identif \
--use_case_id 2 \
--anomaly_case_path home/root/Anomaly\1/block\1/
```

# Customize communication -- Mostly coding 

**You can build your own UC by adding elements to the projects.**

### First : Format your data 

Within */convincesitaw_mllm/synchronized_input_multimodal_data* 

Create your own **SIMD_UC{number}.py** script to read your data and format the proprioception message to the VLM to build your complete json files. It has to inherite from the **SIMD** abstract class. 

### Second : Message to send to VLM

Within */convincesitaw_mllm/inference_message* 

If you want to add extra message to send to the VLM, write your own **message_uc{number}.py** script that inherites from **Message** abstract class. Like for UC2 where we add the scan image as an extra element. 

### Third : Write your prompt

Within */convincesitaw_mllm/prompts* 

Create an new prompt script **prompts_UC{number}** that contains three variables : **SYSTEM_PROMPT**, **USER_PROMPT1**, **USER_PROMPT2**.
The field that changes is the **SYSTEM_PROMPT** where best is to give details about your system, its task, the data input, some known correlations if any and examples of the desire output. 

There is a template of the system prompt and the user prompts :
```
SYSTEM_PROMPT="""
[SYSTEM]:
You are a ...

[TASKS]:
...

[MANIPULATED OBJECTS]:
...

[DATA INPUT]:
The data you will receive is ...

[KNOWN CORRELATIONS]:
...

For your analysis, 
please fill the following JSON
structure with realistic data:
<JSON EMPTY STRUCTURE>

Here is a list of situation descriptions:
<SITUATION LIST>

Here are some examples of correct situations:
---
Previous response:
<POPULATED JSON STRUCTURE>
Correct situation: <CORRESPONDING SITUATION>
---
...
---
"""

USER_PROMPT1="""
Please analyse the data.
NO EXPLANATION IS REQUESTED.
"""

USER_PROMPT2="""
Based on the previous response, pick the correct situation description in the list.
"""
```

### Fourth : Add your class 

Add your new use case to the mappings within *convincesitaw_mllm/inference/Ucs_mapping.py* 
