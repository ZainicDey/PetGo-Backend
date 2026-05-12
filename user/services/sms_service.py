# user/services/sms_service.py
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class SMSService:
    """
    Service for sending SMS messages
    
    To use in production, integrate with any of these providers:
    - Twilio: https://www.twilio.com/docs/sms
    - AWS SNS: https://aws.amazon.com/sns/
    - MessageBird: https://www.messagebird.com/
    - Vonage (Nexmo): https://www.vonage.com/
    - Africa's Talking: https://africastalking.com/
    - TextLocal: https://www.textlocal.com/
    """
    
    @staticmethod
    def send_otp(phone_number, otp):
        """
        Send OTP via SMS to the given phone number
        
        Args:
            phone_number (str): Recipient's phone number (with country code)
            otp (str): 6-digit OTP code
            
        Returns:
            bool: True if successful
            
        Raises:
            Exception: If SMS sending fails
        """
        try:
            # In development mode, just log the OTP
            if settings.DEBUG:
                logger.info(f"[DEV MODE] Sending OTP to {phone_number}")
                logger.info(f"[DEV MODE] OTP Code: {otp}")
                
                # Print to console for easy testing
                print("\n" + "="*50)
                print(f"📱 SMS OTP for {phone_number}")
                print(f"🔑 Code: {otp}")
                print(f"⏰ Expires in: 10 minutes")
                print("="*50 + "\n")
                
                return True
            
            # Production mode - Integrate with actual SMS provider
            # Choose ONE of the following integrations:
            
            # return SMSService._send_via_twilio(phone_number, otp)
            # return SMSService._send_via_aws_sns(phone_number, otp)
            # return SMSService._send_via_messagebird(phone_number, otp)
            # return SMSService._send_via_vonage(phone_number, otp)
            
            # For now, raise error if no provider configured
            raise NotImplementedError(
                "SMS provider not configured. "
                "Please integrate with an SMS provider in production."
            )
            
        except Exception as e:
            logger.error(f"Failed to send SMS to {phone_number}: {str(e)}")
            raise Exception(f"Failed to send OTP: {str(e)}")
    
    @staticmethod
    def _send_via_twilio(phone_number, otp):
        """
        Send SMS via Twilio
        
        Install: pip install twilio
        
        Settings required:
            TWILIO_ACCOUNT_SID = 'your-account-sid'
            TWILIO_AUTH_TOKEN = 'your-auth-token'
            TWILIO_PHONE_NUMBER = '+1234567890'
        """
        try:
            from twilio.rest import Client
            
            client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            
            message = client.messages.create(
                body=f'Your verification code is: {otp}. Valid for 10 minutes.',
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            
            logger.info(f"Twilio SMS sent to {phone_number}. SID: {message.sid}")
            return True
            
        except ImportError:
            logger.error("Twilio package not installed. Run: pip install twilio")
            raise
        except Exception as e:
            logger.error(f"Twilio SMS failed: {str(e)}")
            raise
    
    @staticmethod
    def _send_via_aws_sns(phone_number, otp):
        """
        Send SMS via AWS SNS
        
        Install: pip install boto3
        
        Settings required:
            AWS_ACCESS_KEY_ID = 'your-access-key'
            AWS_SECRET_ACCESS_KEY = 'your-secret-key'
            AWS_REGION = 'us-east-1'
        """
        try:
            import boto3
            
            client = boto3.client(
                'sns',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            
            response = client.publish(
                PhoneNumber=phone_number,
                Message=f'Your verification code is: {otp}. Valid for 10 minutes.',
                MessageAttributes={
                    'AWS.SNS.SMS.SenderID': {
                        'DataType': 'String',
                        'StringValue': 'YourApp'
                    },
                    'AWS.SNS.SMS.SMSType': {
                        'DataType': 'String',
                        'StringValue': 'Transactional'
                    }
                }
            )
            
            logger.info(f"AWS SNS SMS sent to {phone_number}. MessageId: {response['MessageId']}")
            return True
            
        except ImportError:
            logger.error("Boto3 package not installed. Run: pip install boto3")
            raise
        except Exception as e:
            logger.error(f"AWS SNS SMS failed: {str(e)}")
            raise
    
    @staticmethod
    def _send_via_messagebird(phone_number, otp):
        """
        Send SMS via MessageBird
        
        Install: pip install messagebird
        
        Settings required:
            MESSAGEBIRD_API_KEY = 'your-api-key'
        """
        try:
            import messagebird
            
            client = messagebird.Client(settings.MESSAGEBIRD_API_KEY)
            
            message = client.message_create(
                'YourApp',
                phone_number,
                f'Your verification code is: {otp}. Valid for 10 minutes.',
                {'reference': 'OTP'}
            )
            
            logger.info(f"MessageBird SMS sent to {phone_number}. ID: {message.id}")
            return True
            
        except ImportError:
            logger.error("MessageBird package not installed. Run: pip install messagebird")
            raise
        except Exception as e:
            logger.error(f"MessageBird SMS failed: {str(e)}")
            raise
    
    @staticmethod
    def _send_via_vonage(phone_number, otp):
        """
        Send SMS via Vonage (formerly Nexmo)
        
        Install: pip install vonage
        
        Settings required:
            VONAGE_API_KEY = 'your-api-key'
            VONAGE_API_SECRET = 'your-api-secret'
        """
        try:
            import vonage
            
            client = vonage.Client(
                key=settings.VONAGE_API_KEY,
                secret=settings.VONAGE_API_SECRET
            )
            
            sms = vonage.Sms(client)
            
            response = sms.send_message({
                'from': 'YourApp',
                'to': phone_number,
                'text': f'Your verification code is: {otp}. Valid for 10 minutes.',
            })
            
            if response['messages'][0]['status'] == '0':
                logger.info(f"Vonage SMS sent to {phone_number}")
                return True
            else:
                error = response['messages'][0]['error-text']
                raise Exception(f"Vonage error: {error}")
                
        except ImportError:
            logger.error("Vonage package not installed. Run: pip install vonage")
            raise
        except Exception as e:
            logger.error(f"Vonage SMS failed: {str(e)}")
            raise
    
    @staticmethod
    def send_welcome_message(phone_number, username):
        """Send a welcome message after successful registration"""
        message = f"Welcome to OurApp, {username}! Your account has been created successfully."
        
        try:
            if settings.DEBUG:
                logger.info(f"[DEV MODE] Welcome SMS to {phone_number}: {message}")
                return True
            
            # Use the same provider as OTP
            # return SMSService._send_via_twilio(phone_number, message)
            
            return True
        except Exception as e:
            logger.error(f"Failed to send welcome SMS: {str(e)}")
            # Don't raise error for welcome message
            return False