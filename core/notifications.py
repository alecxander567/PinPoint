import firebase_admin
from firebase_admin import credentials, messaging
from firebase_admin.exceptions import FirebaseError
import os
from django.conf import settings

cred = credentials.Certificate(
    os.path.join(settings.BASE_DIR, "serviceAccountKey.json")
)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)


def send_push_notification(token, title, body):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token,
    )
    response = messaging.send(message)
    return response


def notify_owner(item):
    from users.models import User  

    try:
        owner = User.objects.get(id=item.owner_id)
    except User.DoesNotExist:
        return

    if owner.fcm_token:
        try:
            send_push_notification(
                token=owner.fcm_token,
                title="Item Found!",
                body=f"Your item '{item.name}' was reported found.",
            )
        except FirebaseError as e:
            print(f"FCM failed for {owner.email}: {e}")
