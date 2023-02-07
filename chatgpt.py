from log_config import Log
import json, os, openai



def read_config(config_path):
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config



def get_query(query_path, data_path, query_venv_path):
    logging.info(f"Get query.")

    with open(query_path, 'r', encoding = "utf-8") as f:
        prompt1 = f.read()

    with open(query_venv_path, 'r', encoding = "utf-8") as f:
        prompt2 = f.read()

    prompt1 += f"\n    資料存檔的絕對路徑為{data_path}。\n\n"

    prompt1 = prompt1.replace(
        "資料期間:無",
        f"用sys.argv接收命令列參數:\n    1. 起始時間\n    2. 結束時間"
        )
    prompt1 += prompt2

    logging.info(f"<< Question >>\n{prompt1}")

    return prompt1
    



def connect_gpt(openai, api_key, prompt):
    openai.api_key = api_key

    response = openai.Completion.create(
    model = "text-davinci-003",
    prompt = prompt,
    temperature = 0.8,
    max_tokens = 3000,
    )

    response1 = response['choices'][0]['text'].lstrip("\n")
    code, requirements = response1.split("\n2.")
    code = code.replace("1.", "").lstrip("\n").rstrip("\n")
    requirements = requirements.lstrip("\n")

    return code, requirements



def save_file(code, requirements, python_path, requirements_path):
    logging.info(f"Save response python file.")

    with open(python_path, 'w', encoding = "utf-8") as f:
        f.write(code)
    
    with open(requirements_path, 'w', encoding = "utf-8") as f:
        f.write(requirements)

    logging.info(f"Finish!")



def main():
    config = read_config(config_path = "./config.json")

    root = config["root"]
    query_path = root + "/" + config["query_path"]
    data_path = root + "/" + config["data_path"]
    query_venv_path = root + "/" + config["query_venv_path"]
    python_path = root + "/" + config["python_path"]
    requirements_path = root + "/" + config["requirements_path"]
    result_path = root + "/" + config["result_path"]
    api_key = config["api_key"]
    log_path = root + "/" + config["log_path"]
    exe_log_path = root + "/" + config["exe_log_path"]


    log = Log()
    global logging
    logging = log.set_log(filepath = log_path, level = 2, freq = "D", interval = 50)

    prompt = get_query(query_path, data_path, query_venv_path)

    code, requirements = connect_gpt(openai, api_key, prompt)

    save_file(code, requirements, python_path, requirements_path)

    log.shutdown()



if __name__ == "__main__":
    main()