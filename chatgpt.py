from log_config import Log
import os, json, openai



def read_config(config_path):
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config



def get_query(query, data, query_venv):
    logging.info(f"Get query.")

    with open(query, 'r', encoding = "utf-8") as f:
        prompt1 = f.read()

    with open(query_venv, 'r', encoding = "utf-8") as f:
        prompt2 = f.read()

    prompt1 += f"\n    資料存檔的絕對路徑為{data}。\n\n"

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
    code = code.replace("Answer:", "").replace("1.", "").lstrip("\n").rstrip("\n")
    requirements = requirements.lstrip("\n")

    return code, requirements



def save_file(code, package, python, requirements):
    logging.info(f"Save response python file.")

    with open(python, 'w', encoding = "utf-8") as f:
        f.write(code)
    
    with open(requirements, 'w', encoding = "utf-8") as f:
        f.write(package)

    logging.info(f"Finish!")



def main():
    config = read_config(config_path = ".\config.json")

    root = config["root"]
    data_path = os.path.join("data", config["time"])
    query = os.path.join(root, data_path, config["query"])
    data = os.path.join(root, data_path, config["data"])
    query_venv = os.path.join(root, "data", config["query_venv"])
    python = os.path.join(root, data_path, config["python"])
    requirements = os.path.join(root, data_path, config["requirements"])
    # result = os.path.join(root, data_path, config["result"])
    log_path = os.path.join(root, config["log_path"])
    exe_log_path = os.path.join(root, config["exe_log_path"])
    api_key = config["api_key"]

    folder = os.path.join(root, data_path)
    if not os.path.isdir(folder):
        os.makedirs(folder)


    log = Log()
    global logging
    logging = log.set_log(filepath = log_path, level = 2, freq = "D", interval = 50)

    prompt = get_query(query, data, query_venv)

    code, package = connect_gpt(openai, api_key, prompt)

    save_file(code, package, python, requirements)

    log.shutdown()



if __name__ == "__main__":
    main()