from log_config import Log
from traceback import format_exc
from utils import *
import os, shutil, time, sys


log = Log()
logging = log.set_log(name = "run")



def main():
    try:
        # record parameters
        logging.info(f"sys.argv = {sys.argv[1:]}")


        # get basic parameters
        config = read_config(config_path = ".\config.json")
        
        root = config["root"]
        data_path = os.path.join(root, "data", f"{sys.argv[1]}_{sys.argv[2]}")
        query_path = os.path.join(data_path, "queries")
        final_path = os.path.join(data_path, "final")
        src_path = os.path.join(final_path, "resources")
        api_key = config["api_key"]

        

        # create a basic app server
        if not os.path.exists(final_path):
            shutil.copytree(os.path.join(root, "data", "template", "final"), final_path)
        
        
        # initialize and update queries
        if os.path.exists(query_path):
            shutil.rmtree(query_path)
        source_dir = os.path.join(root, "data", "template", "queries")
        shutil.copytree(source_dir, query_path)

        id_, nick_name = update_querys(data_path, query_path)

        
        # generate API by gpt
        responses = ""
        usages = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        query_info = read_config(config_path = os.path.join(query_path, "query_config.json"))

        for file_path, compair in query_info.items():
            responses, usages = get_response(query_path, api_key, responses, usages, file_path, compair)
            time.sleep(1)


        # save related files
        save_response(responses, src_path, id_)
        flag = update_info(final_path, id_, nick_name)
        if flag:
            update_init(src_path, id_)
            update_run(final_path, id_)
        save_status(data_path, "success", usages)

        logging.info("Finish!")


    except:
        logging.error(format_exc())
        save_status(data_path, "fail", 0)


    finally:
        logging.info("-" * 100)
        log.shutdown()



if __name__ == '__main__':
    main()