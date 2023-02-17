from log_config import Log
from traceback import format_exc
from utils import *



try:
    config = read_config(config_path = ".\config.json")

    root = config["root"]
    data_path = os.path.join(root, "data", config["id"])
    data_path1 = os.path.join(data_path, "data")
    run_log_path = os.path.join(root, config["run_log"])
    exe_log_path = os.path.join(root, config["exe_log"])
    api_key = config["api_key"]
    type_ = config["type"]

    folder = os.path.join(root, data_path1)
    if not os.path.isdir(folder):
        os.makedirs(folder)

    
    log = Log()
    logging = activate_log(log, run_log_path)


    total_query, total_response = "", ""

    query = get_query(data_path, data_path1, type_, file_path = "query.txt")
    response = connect_gpt(api_key, query, type_)
    if type_ == "py":
        response_path = os.path.join(data_path1, f"response.{type_}")
    else:
        response_path = os.path.join(data_path, f"response.{type_}")
    save_response(response, response_path)

    total_query += query
    total_response += response

    if type_ == "py":
        query_venv = get_query(data_path, data_path1, type_ = "package", file_path = "..\\query_venv.txt", code = response)
        response_venv = connect_gpt(api_key, query_venv, type_)
        response_venv_path = os.path.join(data_path1, "requirements.txt")
        save_response(response_venv, response_venv_path)

        total_query += query_venv
        total_response += response_venv

        generate_exe(data_path1, response_venv_path, response_path, exe_log_path)
        # save_html(data_path)

    n_tokens = calculate_token(total_query, total_response)
    save_status(data_path, "success", n_tokens)
    logging.info("Finish!")

except:
    logging.error(format_exc())
    save_status(data_path, "fail", 0)

finally:
    logging.info("-"*100)
    log.shutdown()