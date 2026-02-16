Customized UC -- Goes through coding
===========================================

**You can build your own UC by adding elements to the projects.**

First : Format your data 
------------------------

Within */convincesitaw_mllm/synchronized_input_multimodal_data* 

Create your own **SIMD_UC{number}.py** script to read your data and format the proprioception message to the VLM to build all needed directories : images/, video/, csv_images_files/, and maybe other specific ones. It has to inherite from the **SIMD** abstract class. 

Second : Message to send to VLM
--------------------------------

Within */convincesitaw_mllm/inference_message* 

If you want to add extra messages to send to the VLM, write your own **message_uc{number}.py** script that inherites from **Message** abstract class. Like for UC2 where we add the scan image as an extra element, and UC1 where we add an extra text details.

Else return the generic function from the base class.

Third : Write your prompt
-------------------------

Within */convincesitaw_mllm/prompts* 

Create an new prompt script **prompts_UC{number}** that contains three variables : **SYSTEM_PROMPT**, **USER_PROMPT1**, **USER_PROMPT2**.
Within **SYSTEM_PROMPT** the best is to give details about your system, its task, the data input, some known correlations if any and the anomalies list. 

There is a template of the system prompt and the user prompts :

.. code-block:: python

    SYSTEM_PROMPT="""
    [SYSTEM]:
    You are a ...

    [TASKS]:
    ...

    [MANIPULATED OBJECTS]:
    -
    -
    ...

    [DATA INPUT]:
    The data you will receive is:
    - 
    -
    ...

    [KNOWN CORRELATIONS]:
    -
    -
    ...

    [DECISION RULES]:
    -
    -
    ...

    [Actions]:
    1.
    2.
    ...

    [OUTPUT FORMAT]:
    <JSON EMPTY STRUCTURE>
    """

    USER_PROMPT1="""
    You are provided with a batch of data 
    corresponding to one robot action execution.
    ...
    Follow these reasoning steps:
    1. ...
    2. ...
    ...

    Requirements: 
    ...

    Reminder:
    -
    -
    ...
    """

    USER_PROMPT2="""
    You will now be given
    several classification examples...

    --- Classification Examples ---

    -- Example 1: 

    Analysis:
    <ANALYSIS>
    <POPULATED JSON STRUCTURE>
    Correct action:
    <CORRESPONDING ACTION>

    -- Example 2:
    ...

    --- End of Examples ---
    Now classify YOUR previous JSON
    into one action from the system prompt.

    Format:
    <CORRESPONDING ACTION>
    """

Fourth : Add your class 
-----------------------

Add your new use case to the mappings within *convincesitaw_mllm/inference/Ucs_mapping.py* 

