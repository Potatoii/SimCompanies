import settings
from notification.bark import bark_notification
from notification.mail import mail_notification, MailSchema


class Notification:
    def __init__(self):
        self.bark_status = True if settings.notice_config.bark.bark_key else False
        self.mail_status = True if settings.notice_config.mail.username else False

    async def notify(self, message: str):
        """
        通知
        """
        if self.bark_status:
            await bark_notification(message)
        if self.mail_status:
            mail_params = MailSchema(
                mail_from=settings.notice_config.mail.username,
                mail_to=[settings.notice_config.mail.username],
                subject="SimBot",
                content=message,
            )
            await mail_notification(mail_params)


notifier = Notification()

if __name__ == "__main__":
    import asyncio

    asyncio.run(Notification().notify("test"))
