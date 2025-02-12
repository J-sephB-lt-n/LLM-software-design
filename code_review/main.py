"""
CLI script for code review using a local OLLAMA model
"""

import argparse
import pathlib
import sys

import openai

from code_review import constants

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "-b", 
        "--best_practices", 
        type=str,
        help="Comma-separated list indicating which software best practices should be assessed\
 e.g. --best_practices='1,2,5'\
 Run main.py with no arguments to see a list of available options."
    )
    arg_parser.add_argument(
        "-s",
        "--source_code",
        type=pathlib.Path,
        help="File path to single text file containing all code to be assessed\
 (multiple scripts to be dumped in a single file for current state of this program - sorry)\
 I use this tool: https://github.com/J-sephB-lt-n/dot-files-v2/blob/main/command_line_tools/format_file_contents_for_llm.py"
    )
    args = arg_parser.parse_args()

    if args.best_practices is None:
        print("Available options are:")
        for index, (practice_name, practice_description) in enumerate(constants.software_best_practices.items()):
            print(f'[{index}] "{practice_name}" is "{practice_description}"')
        exit()

    best_practice_names: list[str] = list(constants.software_best_practices.keys())
    best_practice_names_to_include: list[str] = [best_practice_names[int(i)] for i in args.best_practices.split(",")]

    print("You have selected the following best practices to include:")
    for practice_name in best_practice_names_to_include:
        print("\t", practice_name)
    program_to_continue: bool = input("Proceed? (only 'yes' will proceed)\n") == "yes"
    if not program_to_continue:
        exit()

    with open(args.source_code, "r", encoding="utf-8") as file:
        code_to_review: str = file.read()

    llm_client = openai.OpenAI(
        base_url="http://localhost:11434/v1/",
        api_key="not-used-but-required",
    )

    for practice_name in best_practice_names_to_include:
        practice_description: str = constants.software_best_practices[practice_name]

        print("###############")
        print(practice_name)
        print("###############")
        
        with open("code_review/prompt.txt", "r", encoding="utf-8") as file:
            prompt: str = file.read()

        prompt = prompt.replace("{{ software_best_practice_name }}", practice_name)
        prompt = prompt.replace("{{ software_best_practice_definition }}", practice_description)
        
        print(prompt)

        prompt = prompt.replace("{{ code_to_review }}", code_to_review)

        for llm_resp in llm_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a wise and experienced software architect",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            model="hf.co/bartowski/DeepSeek-R1-Distill-Qwen-14B-GGUF:Q4_K_M",
            stream=True,
        ):
            sys.stdout.write(llm_resp.choices[0].delta.content or "")
            sys.stdout.flush()
