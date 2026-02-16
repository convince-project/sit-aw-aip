.. _docker-section:

Requirements 
============

Install Docker (for hosted model on server)
-------------------------------------------

**Linux (Ubuntu >= 22.04) -** `docker-documentation`_ **to also check other OSs**

⚠ You need to have sudo rights

.. _docker-documentation: https://docs.docker.com/engine/install/ubuntu/

Uninstall unofficial packages
"""""""""""""""""""""""""""""

.. code-block:: bash

    for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done

Set up
""""""

.. code-block:: bash
    
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

Install packages
""""""""""""""""

.. code-block:: bash

    sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

Start docker services if disabled
"""""""""""""""""""""""""""""""""

.. code-block:: bash

    sudo systemctl status docker
    sudo systemctl start docker

Running without sudo
""""""""""""""""""""

.. code-block:: bash

    sudo usermod -aG docker $USER
    newgrp docker

Verify installation
"""""""""""""""""""

.. code-block:: bash

    docker run hello-world

Install ros2 (humble)
---------------------

Following these instructions :  `ros_doc`_

.. _ros_doc: https://docs.ros.org/en/humble/Installation.html
