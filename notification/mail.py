import os
from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from typing import Optional

import aiosmtplib
from pydantic import BaseModel

import settings
from log_utils import logger

COMMASPACE = ", "


class MailServerSchema(BaseModel):
    """
    邮件服务器
    """

    host: str = settings.mail_config["host"]
    port: int = settings.mail_config["port"]
    username: str = settings.mail_config["username"]
    password: str = settings.mail_config["password"]


class MailSchema(BaseModel):
    mail_server: MailServerSchema = MailServerSchema()  # 邮件服务器
    mail_from: str  # 发件人
    mail_to: list  # 收件人
    cc_to: Optional[list]  # 抄送
    subject: str  # 邮件主题
    content: str  # 邮件内容
    content_images: Optional[dict]  # 邮件内容中的图片
    attachments: Optional[list]  # 附件


async def mail_notification(mail_params: MailSchema) -> dict:
    logger.info(f"进入发送邮件流程")
    # 邮件信息
    mail_message = MIMEMultipart()
    mail_message["From"] = mail_params.mail_from
    mail_message["To"] = COMMASPACE.join(list(set(mail_params.mail_to)))
    mail_message["CC"] = COMMASPACE.join(mail_params.cc_to) if mail_params.cc_to else ""
    mail_message["Subject"] = Header(mail_params.subject, "utf-8")
    mail_message["Date"] = formatdate(localtime=True)
    # 邮件内容
    html_content = MIMEText(mail_params.content, "html", "utf-8")
    mail_message.attach(html_content)
    # 邮件内容图片
    if mail_params.content_images:
        for content_id, image_path in mail_params.content_images.items():
            if image_path:
                image = open(image_path, "rb")
                image_mime = MIMEImage(image.read())
                image_mime.add_header("Content-ID", content_id)
                image.close()
                mail_message.attach(image_mime)
    # 邮件附件
    if mail_params.attachments:
        for attachment in mail_params.attachments:
            attachment_mime = MIMEBase("application", "octet-stream")
            attachment_file = open(attachment, "rb")
            attachment_mime.set_payload(attachment_file.read())
            attachment_file.close()
            # Base64加密成字符串
            encoders.encode_base64(attachment_mime)
            attachment_mime.add_header(
                "Content-Disposition",
                "attachment",
                filename=os.path.basename(attachment),
            )
            mail_message.attach(attachment_mime)
    mailrecord_params = {
        "mail_from": mail_params.mail_from,
        "mail_to": mail_params.mail_to,
        "cc_to": mail_params.cc_to,
        "subject": mail_params.subject,
        "content": mail_params.content,
        "content_images": mail_params.content_images,
        "attachments": mail_params.attachments,
    }
    try:
        async with aiosmtplib.SMTP(
                hostname=mail_params.mail_server.host,
                port=mail_params.mail_server.port,
                username=mail_params.mail_server.username,
                password=mail_params.mail_server.password,
                use_tls=True,
        ) as smtp:
            await smtp.ehlo()
            logger.debug(f"开始登录邮箱")
            await smtp.login(
                mail_params.mail_server.username, mail_params.mail_server.password
            )
            logger.debug(f"登录邮箱成功")
            logger.debug(f"开始发送邮件")
            result = await smtp.sendmail(
                mail_params.mail_from,
                mail_params.mail_to,
                mail_message.as_string(),
                timeout=30,
            )
            logger.info(f"邮件发送成功, {result}")
    except aiosmtplib.SMTPResponseException as e:
        logger.error(f"邮件发送失败: {e}")
        raise e
    except aiosmtplib.SMTPException as e:
        logger.error(f"邮件发送失败: {e}")
        raise e
    return mailrecord_params


if __name__ == "__main__":
    import asyncio

    test_params = MailSchema(
        mail_from=settings.mail_config["username"],
        mail_to=[settings.mail_config["username"]],
        subject="test",
        content="test",
    )
    asyncio.run(mail_notification(test_params))
