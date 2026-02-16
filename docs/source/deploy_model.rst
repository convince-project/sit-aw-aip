VLM deployment
==============

To deploy a VLM and use it, you will need a machine that contains more that 40 GB of Vram and more than 30 GB of cache memory (RAM).

You will have to install :ref:`docker <docker-section>` and  install Nvidia container toolkit by following these `instructions`_.

Once you selected the host machine for the model;

.. _instructions: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html

Install the deploy part
-----------------------

Optional - Clone only the corresponding folder
"""""""""""""""""""""""""""""""""""""""""""""""

**Works with Git > 2.27 and the remote server need to support partial clone filtering**

.. code-block:: bash

    git clone --filter=blob:none --no-checkout https://github.com/convince-project/sit-aw-aip.git
    cd convincesitaw-mllm
    git sparse-checkout init --cone
    git sparse-checkout set /vLLM-hosting
    git checkout

Else clone the whole project and consider only *vLLM-hosting* folder
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. code-block:: bash

    git clone https://gitlab.lri.cea.fr/razane.azrou/convincesitaw-mllm.git
    cd convincesitaw-mllm/vLLM-hosting


Run and build
--------------

The **.env** file allows you to change and define some parameters
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
- **MODEL** : The model to deploy - default Qwen2.5-VL
- **PORT** : Exposed and container port - default 23333
- **GPU_MEMORY_USAGE** : The portion (< 1) of GPU usage allowed to the model given GPU capacities -- default 0.99
- **DOWNLOAD_MODEL_CACHE_DIR** : Machine's directory to download cached model to - default "./.cache/huggingface"

⚠ **Changing the model may need different GPU memory usage or disk capacity to where to download the cached model. It is quite specific to the model, so you may need a more powerful machine**

Then execute **bash file**
""""""""""""""""""""""""""

.. code-block:: bash    

   cd vLLM-hosting
   source deploy_model.sh 

You may need to give execute permissions (on Linux)
"""""""""""""""""""""""""""""""""""""""""""""""""""

.. code-block:: bash    
    sudo chmod +x deploy_model.sh

If your are not using bash you can directly build then run the docker compose in your terminal
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. code-block:: bash

    docker compose build
    docker compose up -d
