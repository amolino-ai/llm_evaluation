import ollama, os
from typing import List
import subprocess, psutil, time


def get_prompt_files(folder_path: str) -> List[str]:
    # Check if the given path is a directory
    files = []
    if not os.path.isdir(folder_path):
        print("The provided path is not a directory.")
        return None

    # List all files in the given directory
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # Check if it is a file and not a directory
        if os.path.isfile(file_path):
            # print(f"\nContents of '{filename}':")
            files.append(file_path)
    return files


def get_prompt(file_path: str) -> str:
    with open(file_path, "r") as file:
        prompt = file.read()
        return prompt


def get_model_response(model_name: str, prompt: str) -> str:
    # start ollama server
    ollama_server_pid = subprocess.Popen(
        ["ollama", "serve"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    # Give the process some time to start
    print("Action: Waiting for the Ollama to start...")
    time.sleep(3)
    print("Action: Ollama started")

    response = ollama.chat(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    ollama_server_pid.terminate()
    try:
        ollama_server_pid.wait(timeout=5)  # Wait for the process to terminate
    except subprocess.TimeoutExpired:
        print("Process did not terminate in time. Killing it.")
        ollama_server_pid.kill()

    output = ollama_server_pid.stdout.read().decode("utf-8")
    error = ollama_server_pid.stderr.read().decode("utf-8")
    print("Action: Ollama stopped")
    return response["message"]["content"], output, error


models = ["llama2", "mistral"]

# print("Models available from Ollama", ollama.list())

prompt_files = get_prompt_files("prompts")
for prompt_file in prompt_files:
    prompt = get_prompt(prompt_file)
    for model in models:
        print("Prompt: ", prompt)
        print("Model: ", model)
        res = get_model_response(model, prompt)
        print("Response: ", res[0])
        print("Output: ", res[1])
        print("Error: ", res[2])
        print(
            "..................................................................................................."
        )
        time.sleep(3)
