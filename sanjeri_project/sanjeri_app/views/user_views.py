# # sanjay_app/views.py

# sanjay_app/views.py

from datetime import timedelta
import secrets
import time
import threading

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.core.cache import cache

from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.models import User
from ..models import CustomUser
import re
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import resend

# ---------------------------------------------------------------------------
User = get_user_model()

# ----------------------------
# OTP Helpers (shared)
# ----------------------------

def _otp_key(purpose: str, email: str) -> str:
    """Build a namespaced cache key so signup/forgot OTPs never clash."""
    return f"otp:{purpose}:{email}"

def _send_email_via_resend(api_key: str, from_email: str, to_email: str, subject: str, body: str):
    """
    Sends email via Resend API. Runs in a background thread so it never
    blocks the Gunicorn worker and avoids 504 Gateway Timeout.
    """
    try:
        resend.api_key = api_key
        resend.Emails.send({
            "from": from_email,
            "to": [to_email],
            "subject": subject,
            "text": body,
        })
        print(f"[Resend] Email sent successfully to {to_email} | Subject: {subject}")
    except Exception as e:
        print(f"[Resend] Email sending FAILED to {to_email}: {e}")


def generate_and_send_otp(email: str, username: str, purpose: str, ttl_seconds: int = 120) -> int:
    """
    Generates a 6-digit OTP, stores it in cache IMMEDIATELY (synchronous),
    then fires the Resend email in a background thread so the view returns
    instantly and never hits the Gunicorn 30s timeout.
    purpose: "signup" | "forgot" | "email_change" | "password_change"
    """
    otp = secrets.randbelow(900000) + 100000  # 100000..999999
    key = _otp_key(purpose, email)
    # Store OTP in cache FIRST — this is instant and must complete before view redirects
    cache.set(key, {"otp": otp, "issued_at": int(time.time())}, ttl_seconds)

    if purpose == "signup":
        subject = "Verify Your Email - SANJERI"
        body = f"""
{'='*55}
                      ✨ SANJERI PERFUMES ✨
                    A Scent Beyond the Soul
{'='*55}

Dear {username},

Thank you for choosing Sanjeri Perfumes! We're thrilled to have you
join our community of fragrance enthusiasts.

{'─'*55}

🔐 YOUR ONE-TIME PASSWORD (OTP)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    {otp}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏰ Valid for: {ttl_seconds // 60} minutes
📅 Issued: {time.strftime('%Y-%m-%d %H:%M:%S')}

{'─'*55}

⚠️  IMPORTANT SECURITY NOTICE:
   • Never share this OTP with anyone, including our support team
   • Sanjeri staff will never ask for your verification code
   • If you didn't request this, please ignore this email
   • For security, this OTP expires after {ttl_seconds // 60} minutes

{'─'*55}

📧 support@sanjeriperfume.com
🌐 www.sanjeriperfume.com

With gratitude,
The Sanjeri Perfumes Team
✨ Experience Luxury, One Drop at a Time ✨

{'='*55}
💌 This is an automated message. Please do not reply to this email.
"""
    elif purpose == "email_change":
        subject = "Verify Email Change - SANJERI"
        body = f"""
{'='*55}
                      ✨ SANJERI PERFUMES ✨
                    A Scent Beyond the Soul
{'='*55}

Dear {username},

You requested to change the email address associated with your Sanjeri Perfumes account.

{'─'*55}

🔐 EMAIL CHANGE VERIFICATION OTP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    {otp}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏰ Valid for: {ttl_seconds // 60} minutes
📅 Issued: {time.strftime('%Y-%m-%d %H:%M:%S')}

{'─'*55}

⚠️  IMPORTANT:
   • This OTP verifies your identity for email change
   • Your current email will remain active until verification
   • Once changed, login with your new email address

{'─'*55}

📧 Email Change Process:
   1. Enter this OTP to verify the change
   2. Confirm your new email address
   3. You'll receive a confirmation email
   4. Use your new email for future logins

{'─'*55}

❌ Didn't request this change?
   Please contact our support team immediately to secure your account:
   📧 security@sanjeriperfume.com

{'─'*55}

Questions about your account?
📧 support@sanjeriperfume.com
🌐 www.sanjeriperfume.com/account

Warm regards,
Account Security Team
Sanjeri Perfumes
✨ Keeping Your Account Safe ✨

{'='*55}
ℹ️  This email was sent because someone requested an email change.
   If this wasn't you, please ignore this message.
"""
    elif purpose == "password_change":
        subject = "Verify Password Change - SANJERI"
        body = f"""
{'='*55}
                      ✨ SANJERI PERFUMES ✨
                    A Scent Beyond the Soul
{'='*55}

Dear {username},

A request was made to change the password for your Sanjeri Perfumes account.

{'─'*55}

🔐 PASSWORD CHANGE VERIFICATION OTP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    {otp}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏰ Valid for: {ttl_seconds // 60} minutes
📅 Issued: {time.strftime('%Y-%m-%d %H:%M:%S')}

{'─'*55}
⚠️  SECURITY NOTICE:
   • This OTP is required to change your password
   • Never share this code with anyone
   • Sanjeri staff will never ask for this code

{'─'*55}

🔒 Password Change Tips:
   • Use a strong password (12+ characters)
   • Include uppercase, lowercase, numbers & symbols
   • Don't reuse passwords from other sites
   • Consider using a password manager

{'─'*55}

✅ Didn't request this change?
   Your account may be at risk. Please:
   1. Log in immediately (using your current password)
   2. Review recent account activity
   3. Contact support if you see anything suspicious

   📧 security@sanjeriperfume.com (Emergency support)

{'─'*55}

Need help creating a strong password?
🌐 www.sanjeriperfume.com/security-guide

Stay safe,
Security Team
Sanjeri Perfumes
✨ Protecting Your Fragrance Journey ✨

{'='*55}
🔒 Remember: A strong password is your first line of defense.
"""
    else:  # forgot password
        subject = "Password Reset OTP - SANJERI"
        body = f"""
{'='*55}
                      ✨ SANJERI PERFUMES ✨
                    A Scent Beyond the Soul
{'='*55}

Dear {username},

We received a request to reset the password for your Sanjeri Perfumes account.

{'─'*55}
{'─'*55}

🔐 PASSWORD RESET OTP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    {otp}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏰ Valid for: {ttl_seconds // 60} minutes
📅 Issued: {time.strftime('%Y-%m-%d %H:%M:%S')}

{'─'*55}

⚠️  SECURITY ALERT:
   • Never share this OTP with anyone
   • This code grants access to your account
   • If you didn't request this reset, your account is safe
   • Consider enabling two-factor authentication for extra security

{'─'*55}

🔧 Next Steps:
   1. Enter this OTP on the verification page
   2. Create a strong, unique password
   3. Log in to your account
   4. Review your recent orders for any unauthorized activity

{'─'*55}

❌ Didn't request this?
   You can safely ignore this email. No changes will be made to
   your account without the OTP verification.

{'─'*55}

Need immediate assistance?
📧 security@sanjeriperfume.com
🌐 www.sanjeriperfume.com/help

Best regards,
Security Team
Sanjeri Perfumes
✨ Protecting Your Fragrance Journey ✨

{'='*55}
🔒 For security reasons, never forward this email to anyone.
"""


    # Fire email in a background thread — view returns instantly, no 504!
    email_thread = threading.Thread(
        target=_send_email_via_resend,
        args=(settings.RESEND_API_KEY, settings.DEFAULT_FROM_EMAIL, email, subject, body),
        daemon=True  # Thread dies with process, no cleanup needed
    )
    email_thread.start()
    print(f"[OTP] Cached OTP for {email} (purpose={purpose}). Email thread started.")
    return otp



def get_otp_record(email: str, purpose: str):
    return cache.get(_otp_key(purpose, email))

def clear_otp(email: str, purpose: str):
    cache.delete(_otp_key(purpose, email))


# ----------------------------
# SIGNUP (with OTP verify + resend)
# ----------------------------

def user_signup(request):
    """
    Step 1: Collect details + password. Do NOT create user yet.
    Send OTP and store form data in session as 'pending_user'.
    """
    ref_code = request.GET.get('ref_code', '')
    
    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm = request.POST.get("confirmPassword")
        phone = request.POST.get("phone")
        agree = request.POST.get("agree")
        referral_code = request.POST.get("referral_code", "").strip()

        username_validator = RegexValidator(
            regex='^[a-zA-Z0-9_]+$',
            message='Only letters, numbers, underscore allowed'
        )
        try:
            username_validator(username)
        except ValidationError as e:
            messages.error(request, f'Username error: {e.message}')
            return redirect("user_signup")
        
        
        if phone:
            phone_validator = RegexValidator(
                regex='^[0-9]{10}$',
                message='Enter valid 10 digit phone number'
            )
            try:
                phone_validator(phone)
            except ValidationError as e:
                messages.error(request, f'Phone error: {e.message}')
                return redirect("user_signup")
        

        if not agree:
            messages.error(request, "You must agree to terms and conditions.")
            return redirect("user_signup")

        if password != confirm:
            messages.error(request, "Password and confirmation do not match.")
            return redirect("user_signup")

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect("user_signup")

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("user_signup")

        # Save data temporarily in session (server-side)
        request.session["pending_user"] = {
            "username": username,
            "email": email,
            "password": password, 
            "phone": phone,
            "status": "active",  # ADD THIS LINE - New users are active by default
            "wallet_balance": 0.00,  # ADD THIS LINE - Start with zero balance
            "referral_code_input": referral_code,
        }
        request.session["otp_email"] = email  # for signup OTP flow

        # Send OTP
        generate_and_send_otp(email,username ,purpose="signup", ttl_seconds=120)
        messages.success(request, "OTP sent to your email. Please verify.")
        return redirect("verify_signup_otp")

    return render(request, "user_signup.html", {"ref_code": ref_code})


def verify_signup_otp(request):
    """
    Step 2: Verify OTP for signup.
    On success: create user using the data from 'pending_user'.
    """
    email = request.session.get("otp_email")
    if not email or not request.session.get("pending_user"):
        messages.error(request, "Session expired. Please sign up again.")
        return redirect("user_signup")

    record = get_otp_record(email, "signup")
    expiry_time = None
    if record:
        # Provide expiry timestamp to the template (UNIX seconds)
        expiry_time = record["issued_at"] + 120

    if request.method == "POST":
        otp_entered = (request.POST.get("otp") or "").strip()
        record = get_otp_record(email, "signup")

        if not record:
            messages.error(request, "OTP expired or not found. Please resend and try again.")
            return redirect("verify_signup_otp")

        saved_otp = str(record["otp"])
        if str(otp_entered) != saved_otp:
            messages.error(request, "Invalid OTP.")
            return redirect("verify_signup_otp")

        # Create the user now with ALL fields including status
        data = request.session.get("pending_user")
        try:
            user = CustomUser.objects.create(
                # first_name=data["first_name"],
                # last_name=data["last_name"],
                username=data["username"],
                email=data["email"],
                phone=data.get("phone"),
                # address=data.get("address"),
                # gender=data.get("gender"),
                status=data.get("status", "active"),  # ADD THIS - status field
                wallet_balance=data.get("wallet_balance", 0.00),  # ADD THIS - wallet field
                password=make_password(data["password"]),
            )

            # Process Referral Code
            referral_code_input = data.get("referral_code_input")
            if referral_code_input:
                try:
                    referring_user = CustomUser.objects.get(referral_code=referral_code_input)
                    user.referred_by = referring_user
                    user.save()
                    
                    # Grant Rewards
                    from sanjeri_app.models.offer_models import ReferralOffer
                    from sanjeri_app.models.wallet import Wallet
                    
                    offer = ReferralOffer.objects.filter(is_active=True).first()
                    # Defaults if no offer config exists
                    referrer_reward = 200
                    referee_reward = 100
                    
                    if offer:
                        if offer.referrer_reward_value > 0:
                            referrer_reward = offer.referrer_reward_value
                        if offer.referee_reward_value > 0:
                            referee_reward = offer.referee_reward_value
                    
                    # Ensure wallets exist
                    referrer_wallet, _ = Wallet.objects.get_or_create(user=referring_user)
                    referee_wallet, _ = Wallet.objects.get_or_create(user=user)
                    
                    # Reward for Referrer
                    if referrer_reward > 0:
                        referrer_wallet.deposit(
                            amount=referrer_reward,
                            reason=f"Referral Bonus (referred {user.username})",
                            transaction_type='DEPOSIT'
                        )
                    
                    # Reward for Referee (New User)
                    if referee_reward > 0:
                        referee_wallet.deposit(
                            amount=referee_reward,
                            reason="Referral Sign-up Bonus",
                            transaction_type='DEPOSIT'
                        )
                        
                except CustomUser.DoesNotExist:
                    pass # Invalid referral code, just ignore
            
        except Exception as e:
            messages.error(request, f"Could not create user: {e}")
            return redirect("user_signup")

        # Cleanup
        clear_otp(email, "signup")
        request.session.pop("pending_user", None)
        request.session.pop("otp_email", None)

        messages.success(request, "Signup successful! You can now log in.")
        return redirect("user_login")

    return render(request, "verify_signup_otp.html", {"expiry_time": expiry_time})


def resend_signup_otp(request):
    email = request.session.get("otp_email")
    pending_user = request.session.get("pending_user")

    if not email or not pending_user:
        messages.error(request, "Session expired. Please sign up again.")
        return redirect("user_signup")

    username = pending_user.get("username")

    generate_and_send_otp(email,username, purpose="signup", ttl_seconds=120)
    messages.success(request, "A new OTP has been sent to your email.")
    return redirect("verify_signup_otp")


# ----------------------------
# LOGIN / LOGOUT
# ----------------------------

def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            # CHECK IF USER IS BLOCKED - CRITICAL SECURITY
            if user.status == 'blocked' or not user.is_active:
                messages.error(request, 'Your account has been blocked. Please contact administrator.')
                return redirect("user_login")
            
            login(request, user)
            
            # REDIRECT BASED ON USER TYPE
            if user.is_staff or user.is_superuser:
                # Admin users go to admin dashboard
                messages.success(request, f'Welcome back, Admin {user.first_name}!')
                return redirect("admin_dashboard")  # Make sure this URL exists
            else:
                # Regular users go to homepage
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect("homepage")
                
        messages.error(request, "Invalid credentials.")
        return redirect("user_login")

    return render(request, "user_login.html")


def user_logout(request):
    logout(request)
    # Clear old messages before adding new one
    storage = messages.get_messages(request)
    for _ in storage:
        pass
    messages.success(request, "Successfully logged out.")
    return redirect("user_login")


# ----------------------------
# FORGOT PASSWORD (OTP + Resend + Reset)
# ----------------------------

def forgot_password(request):
    """
    Step 1: Ask for email. If exists, send OTP for 'forgot' purpose.
    """
    if request.method == "POST":
        email = (request.POST.get("email") or "").strip()
        try:
            user=User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Email not registered.")
            return redirect("forgot_password")

        request.session["reset_email"] = email
        generate_and_send_otp(email,user.username,purpose="forgot", ttl_seconds=120)
        messages.success(request, "OTP sent to your email. Please verify.")
        return redirect("verify_otp")

    return render(request, "forgot_password.html")


def verify_reset_otp(request):
    """
    Step 2: Verify OTP for password reset.
    On success: redirect to reset_password page.
    
    """
    print("DEBUG: verify_reset_otp view called")
    email = request.session.get("reset_email")
    if not email:
        messages.error(request, "Session expired. Please try again.")
        return redirect("forgot_password")

    record = get_otp_record(email, "forgot")
    expiry_time = None
    remaining_seconds = 0
    if record:
        expiry_time = record["issued_at"] + 120
        remaining_seconds = max(0, expiry_time - int(time.time()))
    
    if request.method == "POST":
        otp_entered = (request.POST.get("otp") or "").strip()
        record = get_otp_record(email, "forgot")

        if not record:
            messages.error(request, "OTP expired or not found. Please resend and try again.")
            return redirect("verify_reset_otp")

        if str(otp_entered) != str(record["otp"]):
            messages.error(request, "Invalid OTP.")
            return redirect("verify_otp")

        # Mark verified and proceed to reset form
        request.session["reset_verified"] = True
        clear_otp(email, "forgot")
        messages.success(request, "OTP verified. You can now reset your password.")
        return redirect("reset_password")

    return render(request, "verify_otp.html", {"expiry_time": expiry_time,"remaining_seconds": remaining_seconds,},)  # You can reuse the same template


def resend_reset_otp(request):
    email = request.session.get("reset_email")
    if not email:
        messages.error(request, "Session expired. Please try again.")
        return redirect("forgot_password")

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect("forgot_password")

    generate_and_send_otp(email,user.username ,purpose="forgot", ttl_seconds=120)
    messages.success(request, "A new OTP has been sent to your email.")
    return redirect("verify_otp")


def reset_password(request):
    """
    Step 3: Reset password after OTP verification.
    Requires: session['reset_email'] and session['reset_verified'] == True
    """
    email = request.session.get("reset_email")
    verified = request.session.get("reset_verified", False)

    if not email or not verified:
        messages.error(request, "Unauthorized or expired session.")
        return redirect("forgot_password")

    if request.method == "POST":
        new_password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("reset_password")

        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect("forgot_password")

        # Cleanup session flags
        request.session.pop("reset_email", None)
        request.session.pop("reset_verified", None)

        messages.success(request, "Password reset successfully. Please log in.")
        return redirect("user_login")

    return render(request, "reset_password.html")





