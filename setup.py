import importlib
import json

import settings
from log_utils import logger
from notification.mail import MailServerSchema, MailSchema, mail_notification


async def setup():
    if not settings.user_config["email"]:
        email = input("请输入您的Simcompanies账号: ")
        password = input("请输入您的Simcompanies密码: ")
        while True:
            # use_mail = input("是否使用邮箱通知? 输入'y'表示是，其他输入表示否: ")
            if input("是否使用邮箱通知? 输入'y'表示是，其他输入表示否: ").lower() == "y":
                mail_host = input("请输入smtp的地址[例如: smtp.qq.com]: ")
                mail_port = input("请输入smtp的端口: ")
                mail_username = input("请输入smtp邮箱: ")
                mail_password = input("请输入smtp密码: ")
                mail_server = MailServerSchema(
                    host=mail_host,
                    port=int(mail_port),
                    username=mail_username,
                    password=mail_password,
                )
                test_params = MailSchema(
                    mail_server=mail_server,
                    mail_from=mail_username,
                    mail_to=[mail_username],
                    subject="test",
                    content="test",
                )
                try:
                    result = await mail_notification(test_params)
                    if result and not result[0]:
                        logger.info("测试邮件发送成功, 请查收")
                        if input("是否使用该邮箱通知? 输入'y'表示是，其他输入表示否: ").lower() == "y":
                            pass
                        else:
                            continue
                except Exception as e:
                    logger.error(f"邮件发送失败: {e}")
                    logger.error(f"您输入的邮箱配置为: {mail_server.model_dump_json()}")
                    logger.error(f"请检查邮箱配置是否正确")
                    continue
            else:
                mail_host = ""
                mail_port = ""
                mail_username = ""
                mail_password = ""
            if input("是否使用bark通知? 输入'y'表示是，其他输入表示否: ").lower() == "y":
                bark_key = input("请输入bark的access_key: ")
            else:
                bark_key = ""
            if not mail_username and not bark_key:
                logger.warning("请至少选择一种通知方式")
            else:
                break

        with open(f"{settings.root_path}/config.json", "w") as file:
            file.write(json.dumps({
                "user_config": {
                    "email": email,
                    "password": password
                },
                "mail_config": {
                    "host": mail_host,
                    "port": int(mail_port) if mail_port else "",
                    "username": mail_username,
                    "password": mail_password
                },
                "bark_key": bark_key  # noqa
            }, indent=2))
        logger.info("设置完成，信息已经被保存在config.json文件中。")
        logger.info("如需修改, 请删除config.json文件后重新运行程序。")
        importlib.reload(settings)
