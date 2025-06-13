from src.config import settings
from string import Template


def invitation_email_template(email: str) -> str:
    site_url = settings.SITE_URL
    
    html_template = Template("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Buy-advocate Email</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background-color: #f7f9fc;
            margin: 0;
            padding: 0;
            line-height: 1.6;
        }

        .email-wrapper {
            background-color: #f7f9fc;
            padding: 40px 20px;
            min-height: 100vh;
        }

        .container {
            width: 100%;
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 4px;
            overflow: hidden;
        }

        .header {
            text-align: center;
            margin: 0 auto;
            padding: 40px 40px 20px 40px;
        }

        .header h1 {
            color: #1751D0;
            font-size: 28px;
            font-weight: 700;
            margin: 0;
            letter-spacing: -0.5px;
        }

        .content {
            padding: 20px 40px 40px 40px;
            font-size: 16px;
            color: #374151;
            line-height: 1.6;
        }

        .greeting {
            font-size: 16px;
            color: #374151;
            margin-bottom: 20px;
        }

        .main-text {
            font-size: 16px;
            color: #374151;
            margin-bottom: 30px;
            line-height: 1.6;
        }

        .cta-button {
            display: inline-block;
            background-color: #1751D0;
            color: #ffffff !important;
            padding: 8px 32px;
            text-align: center;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 16px;
            margin: 20px 0;
            min-width: 200px;
            box-shadow: 0 2px 4px rgba(23, 81, 208, 0.2);
            transition: background-color 0.2s ease;
        }

        .cta-button:hover {
            background-color: #1e40af;
        }

        .cta-container {
            text-align: center;
            margin: 30px 0;
        }

        .help-text {
            font-size: 14px;
            color: #6b7280;
            margin: 30px 0 20px 0;
            line-height: 1.5;
        }

        .signature {
            font-size: 16px;
            color: #374151;
            margin-top: 30px;
        }

        .signature .team-name {
            font-weight: 600;
            color: #1751D0;
        }

        .footer {
            background-color: #f9fafb;
            padding: 30px 40px;
            text-align: center;
            border-top: 1px solid #e5e7eb;
        }

        .footer-address {
            font-size: 14px;
            text-align: start;
            color: #6b7280;
            margin-bottom: 15px;
        }

        .footer-brand {
            font-size: 16px;
            font-weight: 600;
            color: #1751D0;
            margin-top: 15px;
        }

        .sub-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .social-links {
            margin-top: 15px;
        }

        .social-links a {
            color: #6b7280;
            text-decoration: none;
            margin: 0 8px;
            font-size: 14px;
            transition: color 0.2s ease;
        }

        .social-links a:hover {
            color: #1751D0;
        }

        .divider {
            border: none;
            height: 1px;
            background-color: #e5e7eb;
            margin: 30px 0;
        }

        @media (max-width: 600px) {
            .email-wrapper {
                padding: 20px 10px;
            }
            
            .container {
                margin: 0;
                border-radius: 0;
            }
            
            .header, .content, .footer {
                padding-left: 20px;
                padding-right: 20px;
            }
            
            .header h1 {
                font-size: 24px;
            }
            
            .cta-button {
                padding: 14px 28px;
                min-width: auto;
                width: 100%;
                box-sizing: border-box;
            }
        }
    </style>
</head>
<body>
    <div class="email-wrapper">
        <div class="header">
            <h1>Buy-advocate</h1>
        </div>

        <div class="container">
            
            <div class="content">
                <div class="greeting">Hi $EMAIL,</div>

                <div class="main-text">
                    You've been invited to join Proptech — your smart platform for finding, assessing, and comparing development-ready sites across Australia.
                </div>

                <div class="main-text">
                    Click below to sign up your account and start exploring properties tailored to your needs:
                </div>

                <div class="cta-container">
                    <a href="$SITE_URL/sign-up" class="cta-button">Confirm Email & Continue</a>
                </div>

                <hr class="divider">

                <div class="help-text">
                    Need help or have questions? Just hit reply — we're here to help.<br>
                    Welcome aboard,
                </div>

                <div class="signature">
                    <span class="team-name">The Proptech Team</span>
                </div>
            </div>

            <div class="footer">
                <div class="footer-address">Proptech, 510 Townsend Street, Canberra CA 94103</div>
                
                <div class="sub-footer">
                    <div class="footer-brand">Proptech</div>
                    <div class="social-links">
                        <a href="#">Twitter</a> | <a href="#">Facebook</a> | <a href="#">LinkedIn</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
""")
    return html_template.safe_substitute(EMAIL=email, SITE_URL=site_url)