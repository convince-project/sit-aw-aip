#SIT-AW  Copyright (C) CEA 2025  Razane Azrou
from convincesitaw_mllm.prompts import sys_prompts_UC1,sys_prompts_UC2,sys_prompts_UC3
from convincesitaw_mllm.synchronized_input_multimodal_data.SIMD_UC1 import UC1
from convincesitaw_mllm.synchronized_input_multimodal_data.SIMD_UC2 import UC2
from convincesitaw_mllm.inference_message.message_uc2 import Message_UC2
from convincesitaw_mllm.inference_message.message_uc1 import Message_UC1

use_case_prompt_map ={
        1:sys_prompts_UC1.SYSTEM_PROMPT,
        2: sys_prompts_UC2.SYSTEM_PROMPT
}

use_case_map = {
        1:UC1(),
        2: UC2()
}

message_callback_map = {
        1: Message_UC1,
        2: Message_UC2
}
