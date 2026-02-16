Inference with VLM 
==================

Installations
--------------

Clone project
"""""""""""""

.. code-block:: bash

    git clone https://github.com/convince-project/sit-aw-aip.git

⚠ **At this stage ignore vLLM-hosting folder**

Build your project - Once 
"""""""""""""""""""""""""

.. code-block:: bash 

    uv sync --frozen

Activate virtual env - everytime you enter the project
""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. code-block:: bash   

    source .venv/bin/activate

.. _generate_data: 

Generate the right data format
------------------------------

**This script is in charge of formatting the data in accordance to what is expected by the model and given some required input and data structure.**

.. code-block:: bash  

    formatData \
    --use_case_id {id} \
    --root_path {root_path}

.. _variables: 

Variables 
"""""""""

**use_case_id** : 1,2 or 3 given CONVINCE Use cases order

**root_path** : root_path to all anomalies data, the folders are structured the following way given the use case; only the *required* fields have to be present before hand :

.. _uc1:

UC1
"""

**Think about sourcing your ROS environment and building any interfaces**

.. code-block:: bash 

    -- root 
    -- Anomaly 1
        -- csv_images_files (will be generated)
                angular_imu_velocity.png
                base_current_velocity.png
                odom_vel.png
                trajectory.png
        -- images (will be generated)
                [all images files]
        -- text_files (will be generated)
                class_action.txt
        -- video (will be generated)
                video.mp4
        ros_file.mcap (required! with this extension!)
    -- Anomaly 2 (same as 1)
    -- Anomaly 3 (same as 1)
    -- (repeat)

.. _uc2:

UC2
"""

.. code-block:: bash

    -- root 
    -- Anomaly 1
        -- block 1
            -- folder 1 (required!)
                    chest_cam_video.mp4
                    proprioception.csv
            -- folder 2 (required!)
                    scan_image.png
            -- csv_images_files (will be generated)
                    graph_image_csv_images_files.png
            -- video (will be generated)
                    video.mp4
            -- images (will be generated)
                    [all images files]
        -- block 2 (same as block1)
        -- block 3 (same as block1)
        -- (repeat)
    -- Anomaly 2 (same as Anomaly 1)
    -- (repeat)

**Csv file columns and representation (elements in brackets represent numbers) - please refer for your data structure**

+---------------+--------------+------------+
| timestamp     | name         | position   |
+===============+==============+============+
| {timestamp_0} | gripper_jaws | {value_0}  |
+---------------+--------------+------------+

Other names in the *name* column can be present, but the **gripper_jaws** has to be.

**Example given** :ref:`uc2 <uc2>` **previously presented data structre** :

.. code-block:: bash 

    formatData \
    --use_case_id 2 \
    --root_path home/root/

Send an identification request to the VLM
-----------------------------------------

If you prefer to use a local VLM - works only with our chosen model
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. code-block:: bash 

    inference_local \
    --use_case_id {id} \
    --anomaly_case_path {root_path_to_one_anomaly_case}


If you prefer the hosted VLM
""""""""""""""""""""""""""""

.. code-block:: bash 

    inference_server \
    --use_case_id {id} \
    --anomaly_case_path {root_path_to_one_anomaly_case}


Hosted VLM variables 
""""""""""""""""""""

There are three environment variables defined in the *.env* at the root. The **SERVER_IP** variable need to be changed to the IP of the distant machine where the model is hosted, else it will consider localhost and result in error.
The two other variables **MODEL** and **PORT** have to correspond with the ones defined when deploying the model. 

Shared variables 
""""""""""""""""

**use_case_id** : 1,2 or 3 given the use case you want to treat within CONVINCE use case.

**anomaly_case_path**: within the selected use case and the :ref:`formatted data <generate_data>`, the root_path to the desired anomaly to treat, where all folders are.

**Example given** :ref:`uc1 <uc1>` **previously presented data structre** :

.. code-block:: bash

    identif \
    --use_case_id 1 \
    --anomaly_case_path home/root/Anomaly\1



