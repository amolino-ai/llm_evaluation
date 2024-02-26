import datetime
import os
import subprocess
import time
from typing import List
import csv
import psutil
import ollama


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

    ps_process = psutil.Process(ollama_server_pid.pid)
    memory_info = ps_process.memory_info()
    memory_usage_mb = memory_info.rss / (1024 * 1024)  # Convert bytes to MB

    ollama_server_pid.terminate()
    try:
        ollama_server_pid.wait(timeout=5)  # Wait for the process to terminate
    except subprocess.TimeoutExpired:
        print("Process did not terminate in time. Killing it.")
        ollama_server_pid.kill()

    output = ollama_server_pid.stdout.read().decode("utf-8")
    error = ollama_server_pid.stderr.read().decode("utf-8")
    print("Action: Ollama stopped")
    return response["message"]["content"], output, error, memory_usage_mb


current_time = datetime.datetime.now()
csv_file_name = f"outputs/run_{current_time.strftime('%Y_%m_%d_%H_%M')}.csv"

with open(csv_file_name, mode="w", newline="") as csv_file:
    csv_writer = csv.writer(csv_file)
    # Write the header row
    csv_writer.writerow(
        ["Name of Model", "Prompt", "Response", "Time Taken", "Memory Usage"]
    )

    models = ["mistral"]
    prompt_files = get_prompt_files("prompts")

    for prompt_file in prompt_files:
        prompt = get_prompt(prompt_file)
        for model in models:
            print("Prompt: ", prompt)
            print("Model: ", model)
            start_time = time.perf_counter()
            res = get_model_response(model, prompt)
            time_taken = time.perf_counter() - start_time
            print("Response: ", res[0])
            print(f"Time taken: {time_taken:0.4f} seconds")
            print(f"Memory usage: {res[3]:0.2f} MB")
            print(
                "..................................................................................................."
            )

            # Write the results as a new row in the CSV file
            csv_writer.writerow(
                [
                    model,
                    prompt,
                    res[0],
                    f"{time_taken:0.4f} seconds",
                    f"{res[3]:0.2f} MB",
                ]
            )

            # Sleep for 3 seconds before processing the next prompt
            time.sleep(3)
