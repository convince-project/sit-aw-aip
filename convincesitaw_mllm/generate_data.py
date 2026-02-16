from convincesitaw_mllm.inference.Ucs_mapping import use_case_map
import tyro


def main(use_case_id:int,root_path:str):

   use_case_map[use_case_id].main(root_path)

def cli():
    tyro.cli(main)
