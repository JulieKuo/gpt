import os, openai, json, datetime
from log_config import Log


log = Log()
logging = log.set_log(name = "util")



def read_config(config_path):
    with open(config_path, 'r') as f:
        config = json.load(f)
        
    return config



def condition(text, value):
    if value["conds"] == "": # 若值為空字串，表示不需要該query，直接以空字串取代query的內容
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
                if isinstance(cond[var], str): # 字串須加上''寫入到txt中
                    cond[var] = f"'{cond[var]}'"

        condition += f'判斷變數{cond["type1"]}{cond["var1"]}是否{cond["operator"]}{cond["type2"]}{cond["var2"]}，將結果指定給變數{cond["cond_id"]}。\n'
    
    value["operators"] = value["operators"].lower().replace("and", "&").replace("or", "|").replace("!", "not").replace("~", "not")
    condition += f'\n對變數data進行條件篩選，返回達成{value["operators"]}的所有列，將結果指定給變數data。'

    text = text.replace("%condition%", condition)

    return text



def statistic(text, value):
    freq = value['freq']
    columns = value['columns']
    combination = value['combination']

    freq_text = f"使用pd.Grouper()指定要分組的時間序列欄位，參數key等於'start_time'，頻率為{freq}，將結果指定給變數freq。\n"
    if combination:
        groupby_text = f"使用groupby()對data的(變數freq和欄位combination、{columns})做分群，將結果指定給變數data。"
    else:
        groupby_text = f"使用groupby()對data的(變數freq和欄位{columns})做分群，將結果指定給變數data。"
    group = freq_text + groupby_text
    
    if (freq == "") & (columns != ""):
        text = text.replace("%group%", group).replace("頻率為", "頻率為秒")
    elif (freq != "") & (columns == ""):
        text = text.replace("%group%", group).replace("和欄位)", ")").replace("、)", ")")
    elif (freq != "") & (columns != ""):
        text = text.replace("%group%", group)
    else:  # 若值皆為空字串，表示不需要該query，直接以空字串取代query的內容
        text = ""

    text = text.replace("%method%", value['method'])

    return text



def update_querys(data_path, query_path):
    input_path = os.path.join(data_path, "input.json")

    logging.info(f"Update querys from {input_path}.")

    # 讀取input.json中的內容
    with open(input_path, 'rb') as f:
        input_ = json.load(f, encoding='cp950')

    for file, value1 in input_.items():
        if file == "nick_name": # 保留nick_name，存到meta_info.json中
            nick_name = value1
            continue
        
        # 讀取初始化的query
        txt_path = os.path.join(query_path, f"{file}.txt")
        with open(txt_path, 'r', encoding = "utf-8") as f:
            text = f.read()
        
        # 以input.json中的內容取代對應query的內容
        if file == "condition":
            text = condition(text, value1)
        elif file == "statistic":
            text = statistic(text, value1)
        else:
            for key2, value2 in value1.items():
                if value2 == "": # 若值為空字串，表示不需要該query，直接以空字串取代query的內容
                    text = ""
                else:
                    if key2 == "id": # id須轉為t_YYYYMMDDhhmmss，作為API的class name使用
                        value2 = "t_" + value2
                        id_ = value2
                        
                    text = text.replace(f"%{key2}%", value2)

        # 儲存更新後的query內容
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

    # 清洗回傳結果
    response1 = response['choices'][0]['text'].lstrip("\n")
    response1 = response1.replace("```python", "").replace("`", "").replace("程式碼：", "").replace("code:", "").strip("\n").strip()

    usage = response["usage"].to_dict()

    return response1, usage



def get_response(query_path, api_key, responses, usages, file_path, compair):
    query = get_query(query_path, file_path)
    if query == "": # 若query沒有內容，不須提問
        logging.info("No query.")
        responses = responses.replace(compair, "")

        return responses, usages
    
    response, usage = connect_gpt(api_key, query)

    # 合併回傳結果至API主程式碼中
    if file_path != "main.txt":
        response = f"{' '*8}" + response.replace("\n", f"\n{' '*8}") # 縮排處理
        responses = responses.replace(compair, f"\n{response}\n")
    else:
        responses += response
    
    # 累計tokens總數
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

    # 檢查meta_info.json是否已存在
    if not os.path.exists(info_path):
        with open(info_path, 'w') as f:
            json.dump({"routes": []}, f)

    # 讀取meta_info.json
    with open(info_path, 'r') as f:
        info = json.load(f)

    flag = False # 是否新增route
    routes = [route["name"] for route in info["routes"]] # 抓出現有routes的name

    # 新增route
    if id_ not in routes:
        new = {
                "nick_name": nick_name,
                "name": id_,
                "api_url": f"/api/r89/report/{id_}"
            }

        info["routes"].append(new)
        flag = True

    info["last_update_time"] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    # 儲存更新後的meta_info.json
    with open(info_path, 'w') as f:
        json.dump(info, f, indent = 4)
    
    return flag



def update_init(src_path, time):
    init_path = os.path.join(src_path, "__init__.py")

    logging.info(f"Update {init_path}.")

    with open(init_path, 'r', encoding = "utf-8") as f:
        code = f.read()

    # 新增package的載入動作至__init__.py
    new = f"from .{time} import {time}\n"
    code = code.replace(new, "") # 必免出現重複的route
    code = new + code

    with open(init_path, 'w', encoding = "utf-8") as f:
        f.write(code)



def update_run(final_path, time):
    run_path = os.path.join(final_path, "run.py")
    
    logging.info(f"Update {run_path}.")

    with open(run_path, 'r', encoding = "utf-8") as f:
        code = f.read()
    
    new = f'\napi.add_resource({time}, "/api/r89/report/{time}")'
    code = code.replace(new, "") # 必免出現重複的route

    # 新增api及route至run.py
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
    
    log.shutdown()