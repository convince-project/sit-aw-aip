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

Format data - generate json (Once on a desired batch of data)
-------------------------------------------------------------

**This script will generate the** :ref:`json_files <variables>` **that will be used by the model**

.. code-block:: bash  

    fData \
    --use_case_id {id} \
    --root_path {root_path}

.. _variables: 
Variables 
"""""""""

**use_case_id** : 1,2 or 3 given CONVINCE Use cases order

**root_path** : root_path to all anomalies data, the folders need to be structured this way given the use case :

.. _uc1:
UC1
"""

.. code-block:: bash 

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

**The excel files columns and representation (elements in brackets represent numbers) - please refer for your data structure** :

*clif_sensors_data.xlsx* :
=================  ===========
                  Data
=================  ===========
{timestamp_0}      {value_0}
=================  ===========

*imu_data_data.xlsx* :
=================  ================  ===========================  ====================  ===============================  =======================  =======================================
                  Orientation        Orientation covariance       Angular velocity      Angular velocity covariance      Linear Acceleration      Linear Acceleration covariance
=================  ================  ===========================  ====================  ===============================  =======================  =======================================
{timestamp_0}      {[list]}          {[list]}                     {[list]}              {[list]}                         {[list]}                 {[list]}
=================  ================  ===========================  ====================  ===============================  =======================  =======================================

*odometrie_data.xlsx*
=================  ================  ====================  ==================  ===============  ================  ==================
                  Pose position      Pose orientation      Pose covariance     Twist linear     Twist angular     Twist covariance
=================  ================  ====================  ==================  ===============  ================  ==================
{timestamp_0}      {[list]}          {[list]}              {[list]}             {[list]}         {[list]}          {[list]}
=================  ================  ====================  ==================  ===============  ================  ==================

*wheel_lift_data.xlsx*
=================  ===========
                  Data
=================  ===========
{timestamp_0}      {value_0}
=================  ===========

.. _uc2:
UC2
"""

.. code-block:: bash

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

**Csv file columns and representation (elements in brackets represent numbers) - please refer for your data structure**

=============  ==============  ===========
timestamp      name            position
=============  ==============  ===========
{timestamp_0}  gripper_jaws    {value_0}
=============  ==============  ===========

Other names in the *name* column can be present, but the **gripper_jaws** has to be.

**Example given** :ref:`uc1 <uc1>` **previously presented data structre** :

.. code-block:: bash 

    fData \
    --use_case_id 1 \
    --root_path home/root/

Send an identification request to the VLM server
------------------------------------------------

.. code-block:: bash 

    identif \
    --use_case_id {id} \
    --anomaly_case_path {root_path_to_one_anomaly_case}

Variables 
"""""""""

There are three environment variables defined in the *.env* at the root. The **SERVER_IP** variable need to be changed to the IP of the distant machine where the model is hosted, else it will consider localhost and result in error.
The two other variables **MODEL** and **PORT** have to correspond with the ones defined when deploying the model. 

**use_case_id** : 1,2 or 3 given the use case you want to treat within CONVINCE use case.

**anomaly_case_path**: within the selected use case and the [formatted data](#format-data---generate-json-once-on-a-desired-batch-of-data), the root_path to the desired anomaly to treat, where a *json_files* folder is. 

**Example given** :ref:`uc2 <uc2>` **previously presented data structre** :

.. code-block:: bash

    identif \
    --use_case_id 2 \
    --anomaly_case_path home/root/Anomaly\1/block\1/
