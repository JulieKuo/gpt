from log_config import Log
from transformers import GPT2TokenizerFast
import os, json, openai
from traceback import format_exc



def read_config(config_path):
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config



def get_query(query, data, query_venv, total_query, type_):
    logging.info("Get query.")

    with open(query, 'r', encoding = "utf-8") as f:
        prompt1 = f.read()

    if type_ == "python":
        with open(query_venv, 'r', encoding = "utf-8") as f:
            prompt2 = f.read()

        data1 = data.replace("\\", "/")
        prompt1 += f"\n    資料存檔的絕對路徑為{data1}。\n\n"

        prompt1 = prompt1.replace(
            "資料期間:無",
            f"用sys.argv接收命令列參數, 參數皆為時間, 在SQL敘述句中需以(')包住參數:\n    1. 起始時間\n    2. 結束時間"
            )
        prompt1 += prompt2

        with open(total_query, 'w', encoding = "utf-8") as f:
            f.write(prompt1)

    return prompt1
    


def connect_gpt(openai, api_key, prompt, raw_response, type_):
    openai.api_key = api_key

    response = openai.Completion.create(
    model = "text-davinci-003",
    prompt = prompt,
    temperature = 0.8,
    max_tokens = 3000,
    )

    response1 = response['choices'][0]['text'].lstrip("\n")

    if type_ == "python":
        with open(raw_response, 'w', encoding = "utf-8") as f:
            f.write(response1)

        code, package = response1.split("\n2.")
        start_index = code.find("import")
        code = code[start_index:].rstrip(" ").rstrip("\n")
        package = package.lstrip(" ").lstrip("\n").rstrip(" ").rstrip("\n")

        return code, package, response1
    else:
        return response1, None, response1



def save_response(code, package, code_path, requirements, type_):
    logging.info("Save response file.")

    with open(code_path, 'w', encoding = "utf-8") as f:
        f.write(code)
    
    if type_ == "python":
        with open(requirements, 'w', encoding = "utf-8") as f:
            f.write(package)



def generate_exe(data_path, requirements, code_path, exe_log_path):
    cmd = f'.\gen_exe.bat "{data_path}" "{requirements}" "{code_path}" "{exe_log_path}"'    
    logging.info(f"Generate exe.\n{cmd}")

    os.system(cmd)



def calculate_token(prompt, response):
    logging.info("Calculate tokens.")
    text = prompt + response
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    n_tokens = len(tokenizer.encode(text))

    return n_tokens



def save_status(result, status, n_tokens):
    logging.info("Save result.")

    result_dict = {
        "status": status,
        "n_tokens": n_tokens
    }

    with open(result, 'w') as f:
        json.dump(result_dict, f, indent = 4)

    logging.info("Finish!")



def main():
    try:
        config = read_config(config_path = ".\config.json")

        root = config["root"]
        data_path = os.path.join(root, "data", config["time"])
        query = os.path.join(data_path, config["query"])
        data = os.path.join(data_path, config["data"])
        query_venv = os.path.join(root, "data", config["query_venv"])
        total_query = os.path.join(data_path, config["total_query"])
        raw_response = os.path.join(data_path, config["raw_response"])
        code_path = os.path.join(data_path, config["code"])
        requirements = os.path.join(data_path, config["requirements"])
        result = os.path.join(data_path, config["result"])
        log_path = os.path.join(root, config["log_path"])
        exe_log_path = os.path.join(root, config["exe_log_path"])
        api_key = config["api_key"]
        type_ = config["type"]

        folder = os.path.join(root, data_path)
        if not os.path.isdir(folder):
            os.makedirs(folder)


        log = Log()
        global logging
        logging = log.set_log(filepath = log_path, level = 2, freq = "D", interval = 50)

        prompt = get_query(query, data, query_venv, total_query, type_)

        
        code, package, response = connect_gpt(openai, api_key, prompt, raw_response, type_)

        save_response(code, package, code_path, requirements, type_)

        if type_ == "python":
            generate_exe(data_path, requirements, code_path, exe_log_path)

        n_tokens = calculate_token(prompt, response)

        save_status(result, "success", n_tokens)
    
    except:
        save_status(result, "fail", 0)
        logging.error(format_exc())

    finally:
        log.shutdown()



if __name__ == "__main__":
    main()