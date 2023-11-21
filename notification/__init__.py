import settings
from notification.bark import bark_notification
from notification.mail import mail_notification, MailSchema


class Notification:
    def __init__(self):
        self.bark_status = True if settings.bark_access_key else False
        self.mail_status = True if settings.mail_config["username"] else False

    async def notification(self, message: str):
        """
        通知
        """
        if self.bark_status:
            await bark_notification(message)
        if self.mail_status:
            mail_params = MailSchema(
                mail_from=settings.mail_config["username"],
                mail_to=[settings.mail_config["username"]],
                subject="SimCompanies",
                content="message",
            )
            await mail_notification(mail_params)


if __name__ == "__main__":
    import asyncio

    asyncio.run(Notification().notification("test"))
