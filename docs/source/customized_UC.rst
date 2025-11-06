Customized UC -- Goes through corresponding
===========================================

**You can build your own UC by adding elements to the projects.**

First : Format your data 
------------------------

Within */convincesitaw_mllm/synchronized_input_multimodal_data* 

Create your own **SIMD_UC{number}.py** script to read your data and format the proprioception message to the VLM to build your complete json files. It has to inherite from the **SIMD** abstract class. 

Second : Message to send to VLM
--------------------------------

Within */convincesitaw_mllm/inference_message* 

If you want to add extra messages to send to the VLM, write your own **message_uc{number}.py** script that inherites from **Message** abstract class. Like for UC2 where we add the scan image as an extra element. 
Else use **message_uc1.py** which is the default.

Third : Write your prompt
-------------------------

Within */convincesitaw_mllm/prompts* 

Create an new prompt script **sys_prompts_UC{number}** that contains three variables : **SYSTEM_PROMPT**.
Within **SYSTEM_PROMPT** the best is to give details about your system, its task, the data input, some known correlations if any and examples of the desire output. 

There is a template of the system prompt and the user prompts :

.. code-block:: python

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

Fourth : Add your class 
-----------------------

Add your new use case to the mappings within *convincesitaw_mllm/inference/Ucs_mapping.py* 

