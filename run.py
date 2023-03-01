from log_config import Log
from traceback import format_exc
from utils import *
import os, shutil, time



def main():
    try:
        config = read_config(config_path = ".\config.json")

        root = config["root"]
        data_path = os.path.join(root, "data", f"{config['group_id']}_{config['project_id']}")
        query_path = os.path.join(data_path, "querys")
        final_path = os.path.join(data_path, "final")
        src_path = os.path.join(final_path, "resources")
        run_log_path = os.path.join(root, config["run_log"])
        api_key = config["api_key"]
        id_ = "t_" + config["id"]
        

        if not os.path.exists(final_path):
            shutil.copytree(os.path.join(root, "data", "final_template"), final_path)
        
        
        if os.path.exists(query_path):
            shutil.rmtree(query_path)
        source_dir = os.path.join(root, "data", "querys_template")
        shutil.copytree(source_dir, query_path)

        
        log = Log()
        logging = activate_log(log, run_log_path)


        update_querys(data_path, query_path)


        usages = {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}
        responses = ""
        
        query_info = {
            "main.txt": "",
            "param.txt": "param()",
            "sql_con.txt": "conn = sql_con()",
            "get_data.txt": "get_data()",
            "statistic.txt": "statistic()",
            "condition.txt": "condition()"
        }

        for file_path, compair in query_info.items():
            responses, usages = get_response(query_path, api_key, responses, usages, file_path, compair)
            time.sleep(1)


        save_response(responses, src_path, id_)
        flag = update_info(final_path, id_)
        if flag:
            update_init(src_path, id_)
            update_run(final_path, id_)
        save_status(data_path, "success", usages)

        logging.info("Finish!")


    except:
        logging.error(format_exc())
        save_status(data_path, "fail", 0)


    finally:
        logging.info("-"*100)
        log.shutdown()



if __name__ == '__main__':
    main()