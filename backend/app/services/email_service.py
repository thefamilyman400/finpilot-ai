"""
Email service for sending emails via SMTP
Handles password reset, email verification, and notification emails
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
import logging
from datetime import datetime

from config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.EMAIL_FROM
        self.enabled = settings.ENABLE_EMAIL_NOTIFICATIONS
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """
        Send an email
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email body
            text_content: Plain text alternative (optional)
        
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.enabled:
            logger.warning(f"Email notifications disabled. Skipping email to {to_email}")
            return False
        
        if not self.smtp_user or not self.smtp_password:
            logger.error("SMTP credentials not configured. Cannot send email.")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["From"] = self.from_email
            msg["To"] = to_email
            msg["Subject"] = subject
            
            # Attach plain text and HTML parts
            if text_content:
                msg.attach(MIMEText(text_content, "plain"))
            msg.attach(MIMEText(html_content, "html"))
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error while sending email to {to_email}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {str(e)}")
            return False
    
    def send_password_reset_email(self, email: str, reset_token: str, frontend_url: str = None) -> bool:
        """
        Send password reset email
        
        Args:
            email: Recipient email
            reset_token: JWT reset token
            frontend_url: Frontend URL for reset link (default from config)
        
        Returns:
            True if sent successfully
        """
        if frontend_url is None:
            frontend_url = settings.FRONTEND_URL if hasattr(settings, 'FRONTEND_URL') else "http://localhost:3000"
        
        reset_link = f"{frontend_url}/auth/reset-password?token={reset_token}"
        
        # Plain text version
        text_content = f"""
Hello,

You requested a password reset for your FinPilot AI account.

Click the link below to reset your password:
{reset_link}

This link will expire in 1 hour.

If you did not request this, please ignore this email.

Best regards,
FinPilot AI Team
"""
        
        # HTML version
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #f0f4f8; padding: 20px; text-align: center; border-radius: 5px; margin-bottom: 20px; }}
        .header h1 {{ margin: 0; color: #1e40af; }}
        .content {{ padding: 20px; background-color: #f9fafb; border-radius: 5px; }}
        .button {{ display: inline-block; padding: 10px 20px; margin: 20px 0; background-color: #1e40af; color: white; text-decoration: none; border-radius: 5px; }}
        .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
        .warning {{ background-color: #fef3c7; padding: 10px; border-left: 4px solid #f59e0b; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>FinPilot AI</h1>
            <p>Password Reset Request</p>
        </div>
        
        <div class="content">
            <p>Hello,</p>
            
            <p>You requested a password reset for your FinPilot AI account.</p>
            
            <p>Click the button below to reset your password:</p>
            
            <a href="{reset_link}" class="button">Reset Password</a>
            
            <p>Or copy and paste this link in your browser:</p>
            <p style="word-break: break-all; background-color: #e5e7eb; padding: 10px; border-radius: 3px;">{reset_link}</p>
            
            <div class="warning">
                <strong>Note:</strong> This link will expire in 1 hour. If you did not request this password reset, please ignore this email.
            </div>
            
            <p>If you have any questions, please contact our support team.</p>
            
            <p>Best regards,<br>FinPilot AI Team</p>
        </div>
        
        <div class="footer">
            <p>&copy; {datetime.now().year} FinPilot AI. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""
        
        return self.send_email(
            to_email=email,
            subject="Reset Your FinPilot AI Password",
            html_content=html_content,
            text_content=text_content,
        )
    
    def send_email_verification_email(self, email: str, verification_token: str, frontend_url: str = None) -> bool:
        """
        Send email verification email
        
        Args:
            email: Recipient email
            verification_token: JWT verification token
            frontend_url: Frontend URL for verification link
        
        Returns:
            True if sent successfully
        """
        if frontend_url is None:
            frontend_url = settings.FRONTEND_URL if hasattr(settings, 'FRONTEND_URL') else "http://localhost:3000"
        
        verify_link = f"{frontend_url}/auth/verify-email/{verification_token}"
        
        # Plain text version
        text_content = f"""
Hello,

Thank you for registering with FinPilot AI!

Click the link below to verify your email address:
{verify_link}

This link will expire in 24 hours.

Best regards,
FinPilot AI Team
"""
        
        # HTML version
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #f0f4f8; padding: 20px; text-align: center; border-radius: 5px; margin-bottom: 20px; }}
        .header h1 {{ margin: 0; color: #1e40af; }}
        .content {{ padding: 20px; background-color: #f9fafb; border-radius: 5px; }}
        .button {{ display: inline-block; padding: 10px 20px; margin: 20px 0; background-color: #1e40af; color: white; text-decoration: none; border-radius: 5px; }}
        .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>FinPilot AI</h1>
            <p>Verify Your Email</p>
        </div>
        
        <div class="content">
            <p>Hello,</p>
            
            <p>Thank you for registering with FinPilot AI!</p>
            
            <p>Click the button below to verify your email address:</p>
            
            <a href="{verify_link}" class="button">Verify Email</a>
            
            <p>Or copy and paste this link in your browser:</p>
            <p style="word-break: break-all; background-color: #e5e7eb; padding: 10px; border-radius: 3px;">{verify_link}</p>
            
            <p>This link will expire in 24 hours.</p>
            
            <p>If you did not create this account, please ignore this email.</p>
            
            <p>Best regards,<br>FinPilot AI Team</p>
        </div>
        
        <div class="footer">
            <p>&copy; {datetime.now().year} FinPilot AI. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""
        
        return self.send_email(
            to_email=email,
            subject="Verify Your FinPilot AI Email",
            html_content=html_content,
            text_content=text_content,
        )


# Create a singleton instance
email_service = EmailService()
