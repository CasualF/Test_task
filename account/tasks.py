from config.celery import app
from django.core.mail import send_mail
from datetime import datetime
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken


@app.task(bind=True)
def send_activation_email(self, email, code):
    subject = 'Activation code'
    message = (f'Click the link in order to activate your account\n'
               f'http://16.171.174.219/api/account/activate/?c={code}')
    send_mail(
        subject=subject,
        message=message,
        from_email='dastan12151@gmail.com',
        recipient_list=(email,),
        fail_silently=True
    )
    return 'Activation code was sent'


@app.task(bind=True)
def clear_tokens(self):
    # When logout is done, tokens go into the blacklist and saved in database
    # Celery-beat was implemented in order to clear expired tokens

    BlacklistedToken.objects.filter(token__expires_at__lt=datetime.now()).delete()
    OutstandingToken.objects.filter(expires_at_lt=datetime.now()).delete()

    return 'Expired tokens were deleted'
