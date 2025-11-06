#SIT-AW  Copyright (C) CEA 2025  Razane Azrou
from convincesitaw_mllm.inference.Ucs_mapping import use_case
import tyro


def main(use_case_id:int,root_path:str):

   use_case[use_case_id].main(root_path)

def cli():
    tyro.cli(main)
