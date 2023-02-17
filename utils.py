import os, openai, json
from transformers import GPT2TokenizerFast
import pandas as pd



def activate_log(log, run_log_path):
    global logging
    logging = log.set_log(filepath = run_log_path, level = 2, freq = "D", interval = 50)

    return logging



def read_config(config_path):
    with open(config_path, 'r') as f:
        config = json.load(f)
        
    return config



def get_import(code):
    code_line = code.splitlines(True)

    imports = []
    for line in code_line:
        line = line.strip(" ")
        
        if line.startswith("import") or line.startswith("from"):
            imports.append(line)

    imports = "".join(imports)

    return imports



def get_query(data_path, data_path1, type_, file_path, code = ""):
    query_path = os.path.join(data_path, file_path)
    
    logging.info(f"Get query from {query_path}.")

    request_path = file_path.replace("..\\", "").replace("query", "")
    request_path = os.path.join(data_path1, f"request{request_path}")

    with open(query_path, 'r', encoding = "utf-8") as f:
        prompt1 = f.read()

    if type_ == "py":
        csv_path = os.path.join(data_path, "data.csv")
        csv_path = csv_path.replace("\\", "/")
        html_path = csv_path.replace(".csv", ".html")
        prompt1 = prompt1.replace("file_path_csv", csv_path).replace("file_path_html", html_path)

    elif type_ == "package":
        imports = get_import(code)
        prompt1 = prompt1.replace("{packages}", imports)

    with open(request_path, 'w', encoding = "utf-8") as f:
        f.write(prompt1)


    return prompt1



def connect_gpt(api_key, query_py, type_):
    logging.info("Get response.")

    openai.api_key = api_key

    response = openai.Completion.create(
        model = "text-davinci-003",
        prompt = query_py,
        temperature = 0.2,
        max_tokens = 3000,
        )

    response1 = response['choices'][0]['text'].lstrip("\n")
    if type_ == "py":
        response1 = response1.replace("```python", "").replace("`", "").strip("\n").strip()

    return response1



def save_response(response, response_path):
    logging.info("Save response file.")

    with open(response_path, 'w', encoding = "utf-8") as f:
        f.write(response)



def generate_exe(data_path1, response_venv_path, response_py_path, exe_log_path):
    cmd = f'.\gen_exe.bat "{data_path1}" "{response_venv_path}" "{response_py_path}" "{exe_log_path}"'    
    logging.info(f"Generate exe.\n{cmd}")

    os.system(cmd)



def save_html(data_path, max_row = 20):
    logging.info("Save html.")

    csv_path = os.path.join(data_path, "data.csv")
    html_path =  os.path.join(data_path, "data.html")

    df = pd.read_csv(csv_path)
    html_table = df.iloc[:max_row].to_html()

    with open(html_path, 'w') as f:
        f.write(html_table)



def calculate_token(prompt, response):
    logging.info("Calculate tokens.")
    text = prompt + response
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    n_tokens = len(tokenizer.encode(text))

    return n_tokens



def save_status(data_path, status, n_tokens):
    logging.info("Save result.")

    result_dict = {
        "status": status,
        "n_tokens": n_tokens
    }

    result_path = os.path.join(data_path, "result.json")
    with open(result_path, 'w') as f:
        json.dump(result_dict, f, indent = 4)