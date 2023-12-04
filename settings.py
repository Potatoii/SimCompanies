import json
import os.path

root_path = os.path.dirname(os.path.abspath(__file__))
log_name = "SimCompanies.log"
stdout_level = "INFO"
file_level = "INFO"

if not os.path.exists(os.path.join(root_path, "config.json")):
    with open(os.path.join(root_path, "config.json"), "w") as file:
        file.write(json.dumps({
            "user_config": {
                "email": "",
                "password": ""},
            "mail_config": {
                "host": "",
                "port": "",
                "username": "",
                "password": ""
            },
            "bark_key": ""
        }, indent=2))

json_config = json.loads(open(os.path.join(root_path, "config.json"), "r", encoding="utf-8").read())

user_config = json_config["user_config"]
mail_config = json_config["mail_config"]
bark_key = json_config["bark_key"]
