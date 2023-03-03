import os, openai, json, datetime



def read_config(config_path):
    with open(config_path, 'r') as f:
        config = json.load(f)
        
    return config



def activate_log(log, run_log_path):
    global logging
    logging = log.set_log(filepath = run_log_path, level = 2, freq = "D", interval = 50)

    return logging



def condition(text, value):
    if value["conds"] == "":
        return ""
    
    condition = ""
    for cond in value["conds"]:
        for i in range(1, 3):
            type_ = f"type{i}"
            var = f"var{i}"
            if cond[type_] == "欄位":
                cond[type_] = "data的" + cond[type_]
            elif cond[type_] == "custom":
                cond[type_] = ""
                if isinstance(cond[var], str):
                    cond[var] = f"'{cond[var]}'"

        condition += f'判斷{cond["type1"]}{cond["var1"]}是否{cond["operator"]}{cond["type2"]}{cond["var2"]}，將結果指定給變數{cond["cond_id"]}。\n'

    condition += f'\n對data進行條件篩選，返回達成{value["operators"]}的所有列，將結果指定給變數data。'

    text = text.replace("%condition%", condition)

    return text



def update_querys(data_path, query_path):
    input_path = os.path.join(data_path, "input.json")

    logging.info(f"Update querys from {input_path}.")

    with open(input_path, 'rb') as f:
        input_ = json.load(f, encoding='cp950')

    for file, value1 in input_.items():
        if file == "nick_name":
            nick_name = value1
            continue

        txt_path = os.path.join(query_path, f"{file}.txt")
        with open(txt_path, 'r', encoding = "utf-8") as f:
            text = f.read()
        
        if file == "condition":
            text = condition(text, value1)
        else:
            for key2, value2 in value1.items():
                if value2 == "":
                    text = ""
                else:
                    if key2 == "id":
                        value2 = "t_" + value2
                        id_ = value2
                        
                    text = text.replace(f"%{key2}%", value2)

        with open(txt_path, 'w', encoding = "utf-8") as f:
            f.write(text)
    
    return id_, nick_name



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
    if query == "":
        logging.info("No query.")
        responses = responses.replace(compair, "")

        return responses, usages
    
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



def update_info(final_path, id_, nick_name):    
    info_path = os.path.join(final_path, 'meta_info.json')
    
    logging.info(f"Update {info_path}.")

    if not os.path.exists(info_path):
        with open(info_path, 'w') as f:
            json.dump({"routes": []}, f)

    with open(info_path, 'r') as f:
        info = json.load(f)

    flag = False
    routes = [route["name"] for route in info["routes"]]
    if id_ not in routes:
        new = {
                "nick_name": nick_name,
                "name": id_,
                "api_url": f"/api/r89/report/{id_}"
            }

        info["routes"].append(new)
        flag = True

    info["last_update_time"] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    with open(info_path, 'w') as f:
        json.dump(info, f, indent = 4)
    
    return flag



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



def save_status(data_path, status, usage):
    result_path = os.path.join(data_path, "result.json")

    logging.info(f"Save result under {result_path}.")

    result_dict = {
        "status": status,
        "usage": usage
    }

    with open(result_path, 'w') as f:
        json.dump(result_dict, f, indent = 4)