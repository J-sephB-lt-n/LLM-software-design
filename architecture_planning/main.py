import argparse
import sys

import openai

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-c", "--code_language_name", required=True)
    arg_parser.add_argument("-p", "--project_goals", required=True)
    args = arg_parser.parse_args()

    with open("architecture_planning/prompt.txt", "r", encoding="utf-8") as file:
        prompt: str = file.read()

    prompt = prompt.replace("{{ code_language_name }}", args.code_language_name)
    prompt = prompt.replace("{{ project_goals }}", args.project_goals)

    llm_client = openai.OpenAI(
        base_url="http://localhost:11434/v1/",
        api_key="not-used-but-required",
    )

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
