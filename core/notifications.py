import firebase_admin
from firebase_admin import credentials, messaging
from firebase_admin.exceptions import FirebaseError
import os
import json
import base64
from django.conf import settings


def _init_firebase():
    if not firebase_admin._apps:
        firebase_cred_b64 = os.getenv("FIREBASE_SERVICE_ACCOUNT")
        if firebase_cred_b64:
            firebase_cred_json = json.loads(base64.b64decode(firebase_cred_b64))
            cred = credentials.Certificate(firebase_cred_json)
        else:
            cred = credentials.Certificate(
                os.path.join(settings.BASE_DIR, "serviceAccountKey.json")
            )
        firebase_admin.initialize_app(cred)


def send_push_notification(token, title, body):
    _init_firebase()
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=token,
    )
    return messaging.send(message)


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
