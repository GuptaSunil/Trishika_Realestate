# Email Configuration Setup Guide

## Overview
The application is now configured to send enquiry notifications to your email (`guPta.sunil561@gmail.com`) and send confirmation emails to enquiry submitters.

## Quick Setup for Gmail

### Step 1: Enable 2-Factor Authentication
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Step Verification if not already enabled
3. You'll need this to generate an app password

### Step 2: Generate App Password
1. In Google Account, go to **Security** → **App passwords**
    - (Only appears if 2FA is enabled)
2. Select **Mail** and **Windows Computer** (or your device)
3. Google will generate a 16-character password
4. **Copy this password** (you'll need it next)

### Step 3: Configure Environment Variables
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   (On Windows: `copy .env.example .env`)

2. Edit `.env` and update:
   ```
   MAIL_USERNAME=your-gmail@gmail.com
   MAIL_PASSWORD=xxxx-xxxx-xxxx-xxxx  # Your 16-char app password
   ```

3. **Never commit `.env` to version control** - add to `.gitignore`

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Run the App
**Linux/macOS:**
```bash
bash deploy.sh
```

**Windows PowerShell:**
```powershell
.\deploy.ps1
```

## How It Works
- When someone submits an enquiry form, two emails are sent:
  1. **Admin notification** → `guPta.sunil561@gmail.com` with full enquiry details
  2. **Confirmation email** → Enquiry submitter with their query details

## Using Other Email Providers

### Gmail Workspace / Corporate Email
- MAIL_SERVER: `smtp.gmail.com` (same)
- MAIL_PORT: `587`
- MAIL_USERNAME: your full email
- MAIL_PASSWORD: Your app-specific password

### Outlook/Hotmail
- MAIL_SERVER: `smtp-mail.outlook.com`
- MAIL_PORT: `587`
- MAIL_USE_TLS: `true`

### Custom SMTP Server
Update `.env` with your provider's SMTP details.

## Troubleshooting

**"Authentication failed" error:**
- Verify MAIL_USERNAME and MAIL_PASSWORD in `.env`
- Check 2FA is enabled on your Google account
- Regenerate app password if needed

**"Connection refused" error:**
- Check MAIL_SERVER and MAIL_PORT are correct
- Verify firewall allows outbound port 587

**Emails not sending but no error:**
- Check Flask logs for errors
- Verify email addresses are valid
- Check MAIL_USE_TLS is `true` for port 587

## Testing Email (Optional)
To test email locally without GUI:
```bash
python -c "
from app import app, mail, send_enquiry_email
with app.app_context():
    send_enquiry_email('Test User', 'test@example.com', '9999999999', 'Test Property', 'Test message')
    print('Test email sent!')
"
```

## Production Deployment
For production servers (AWS, Heroku, etc.):
1. Set environment variables in your hosting platform
2. Use environment-specific email configurations
3. Consider using dedicated email services (SendGrid, AWS SES) for reliability
