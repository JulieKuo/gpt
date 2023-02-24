import os, openai, json, datetime



def read_config(config_path):
    with open(config_path, 'r') as f:
        config = json.load(f)
        
    return config



def activate_log(log, run_log_path):
    global logging
    logging = log.set_log(filepath = run_log_path, level = 2, freq = "D", interval = 50)

    return logging



def update_querys(data_path, query_path):
    input_path = os.path.join(data_path, "input.json")

    logging.info(f"Update querys from {input_path}.")

    with open(input_path, 'rb') as f:
        input_ = json.load(f, encoding='cp950')

    for file, value1 in input_.items():
        txt_path = os.path.join(query_path, f"{file}.txt")
        with open(txt_path, 'r', encoding = "utf-8") as f:
            text = f.read()
        
        for key2, value2 in value1.items():
            text = text.replace(f"{key2}", value2)

        with open(txt_path, 'w', encoding = "utf-8") as f:
            f.write(text)



def get_query(query_path, file_path):
    query_path = os.path.join(query_path, file_path)
    
    logging.info(f"Get query from {query_path}.")

    with open(query_path, 'r', encoding = "utf-8") as f:
        prompt1 = f.read()

    return prompt1



def connect_gpt(api_key, query):
    logging.info("Get response from openai.")

    openai.api_key = api_key

    response = openai.Completion.create(
        model = "text-davinci-003",
        prompt = query,
        temperature = 0.2,
        max_tokens = 3000,
        )

    response1 = response['choices'][0]['text'].lstrip("\n")
    response1 = response1.replace("```python", "").replace("`", "").replace("程式碼：", "").strip("\n").strip()

    usage = response["usage"].to_dict()
    # logging.info(usage)

    return response1, usage



def get_response(query_path, api_key, responses, usages, file_path, compair):
    query = get_query(query_path, file_path)
    response, usage = connect_gpt(api_key, query)

    if file_path != "main.txt":
        response = f"{' '*8}" + response.replace("\n", f"\n{' '*8}")
        responses = responses.replace(compair, f"\n{response}\n")
    else:
        responses += response
    
    for key in usages.keys():
        usages[key] += usage[key]

    return responses, usages




def save_response(response, src_path, time):
    api_path = os.path.join(src_path, f"{time}.py")

    logging.info(f"Save response under {api_path}.")

    with open(api_path, 'w', encoding = "utf-8") as f:
        f.write(response)



def update_init(src_path, time):
    init_path = os.path.join(src_path, "__init__.py")

    logging.info(f"Update {init_path}.")

    with open(init_path, 'r', encoding = "utf-8") as f:
        code = f.read()

    new = f"from .{time} import {time}\n"
    code = code.replace(new, "")
    code = new + code

    with open(init_path, 'w', encoding = "utf-8") as f:
        f.write(code)



def update_run(final_path, time):
    run_path = os.path.join(final_path, "run.py")
    
    logging.info(f"Update {run_path}.")

    with open(run_path, 'r', encoding = "utf-8") as f:
        code = f.read()
    
    new = f'\napi.add_resource({time}, "/api/r89/report/{time}")'
    code = code.replace(new, "")

    string = "Api(server)\n\n\n"
    index = code.find(string)
    code = code[:index] + string + new + code[index:].replace(string, "")

    with open(run_path, 'w', encoding = "utf-8") as f:
        f.write(code)



def update_info(final_path, time):    
    info_path = os.path.join(final_path, 'meta_info.json')
    
    logging.info(f"Update {info_path}.")

    if not os.path.exists(info_path):
        with open(info_path, 'w') as f:
            json.dump({"routes": []}, f)

    with open(info_path, 'r') as f:
        info = json.load(f)

    routes = [route["name"] for route in info["routes"]]
    if time not in routes:
        new = {
                "name": time,
                "api_url": f"/api/r89/report/{time}"
            }

        info["routes"].append(new)
    info["last_update_time"] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    with open(info_path, 'w') as f:
        json.dump(info, f, indent = 4)



def save_status(data_path, status, usage):
    result_path = os.path.join(data_path, "result.json")

    logging.info(f"Save result under {result_path}.")

    result_dict = {
        "status": status,
        "usage": usage
    }

    with open(result_path, 'w') as f:
        json.dump(result_dict, f, indent = 4)