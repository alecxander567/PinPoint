from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import User, PasswordResetToken, BugReport
from .serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import EmailMessage
from django.conf import settings
import logging
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)


@api_view(["POST"])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "User created successfully"}, status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED
        )

    if user.check_password(password):
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user_id": str(user.id),
                "name": user.name,
            }
        )

    return Response(
        {"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(["POST"])
def logout(request):
    return Response({"message": "Logout successful, delete the token on client side."})


@api_view(["POST"])
def forgot_password(request):
    email = request.data.get("email")

    if not email:
        return Response(
            {"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(email=email)

        PasswordResetToken.objects.filter(user=user, used=False).delete()

        reset_token = PasswordResetToken.objects.create(user=user)

        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token.token}"

        email_message = EmailMessage(
            subject="Reset your Item Finder password",
            body=(
                f"Hi {user.name},\n\n"
                f"Click the link below to reset your password. "
                f"This link expires in 1 hour.\n\n"
                f"{reset_link}\n\n"
                f"If you didn't request this, you can safely ignore this email."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email_message.send()

        logger.info(f"Password reset link sent to {email} | Token: {reset_token.token}")

    except User.DoesNotExist:
        logger.info(f"Password reset requested for non-existent email: {email}")
        pass
    except Exception as e:
        logger.error(f"SMTP ERROR: {str(e)}")
        return Response({"error": str(e)}, status=500)

    return Response(
        {"message": "If that email is registered, a reset link has been sent."}
    )


@api_view(["POST", "OPTIONS"])
def reset_password(request):
    if request.method == "OPTIONS":
        return Response(status=status.HTTP_200_OK)

    token_str = request.data.get("token")
    new_password = request.data.get("password")

    if not token_str:
        return Response({"error": "Token is required."}, status=400)

    if not new_password:
        return Response({"error": "Password is required."}, status=400)

    if len(new_password) < 8:
        return Response(
            {"error": "Password must be at least 8 characters."}, status=400
        )

    try:
        reset_token = PasswordResetToken.objects.get(token=token_str)
    except PasswordResetToken.DoesNotExist:
        return Response({"error": "Invalid or expired reset link."}, status=400)

    if not reset_token.is_valid():
        return Response(
            {"error": "This reset link has expired or already been used."}, status=400
        )

    try:
        reset_token.user.set_password(new_password)
        reset_token.user.save()

        reset_token.used = True
        reset_token.save()

        return Response({"message": "Password reset successful. You can now log in."})
    except Exception as e:
        print("Unexpected error during reset:", str(e))
        return Response({"error": "Server error during password reset."}, status=500)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    user.name = request.data.get("name", user.name)
    user.messenger_link = request.data.get("messenger_link", user.messenger_link)

    new_password = request.data.get("password")
    if new_password:
        if len(new_password) < 8:
            return Response(
                {"error": "Password must be at least 8 characters."}, status=400
            )
        user.set_password(new_password)

    user.save()
    return Response({"message": "Profile updated successfully."})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_profile(request):
    user = request.user

    return Response(
        {
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "messenger_link": user.messenger_link,
            "created_at": user.created_at,
        }
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_account(request):
    user = request.user

    user.delete()

    return Response(
        {"message": "Account deleted successfully"}, status=status.HTTP_200_OK
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def report_bug(request):
    user = request.user
    message = request.data.get("message")

    if not message:
        return Response(
            {"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    bug = BugReport.objects.create(user=user, message=message)

    EmailMessage(
        subject=f"Bug Report from {user.name}",
        body=(f"From: {user.name} ({user.email})\n\n" f"Message:\n{message}"),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.EMAIL_HOST_USER],  # your email
    ).send(fail_silently=True)

    return Response(
        {"message": "Bug report submitted successfully", "bug_id": str(bug.id)},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
def save_fcm_token(request):
    user = User.objects.get(id=request.data["user_id"])
    user.fcm_token = request.data["token"]
    user.save()

    return Response({"message": "Token saved"})
