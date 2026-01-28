"""
Email alerting service
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dags.utils import config


class EmailAlertService:
    """
    Service for sending email alerts
    """
    
    def __init__(self, smtp_server: str = None, smtp_port: int = None, 
                 sender_email: str = None, sender_password: str = None):
        """
        Initialize email service
        Uses environment variables or provided credentials
        """
        self.smtp_server = smtp_server or getattr(config, 'SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = smtp_port or getattr(config, 'SMTP_PORT', 587)
        self.sender_email = sender_email or getattr(config, 'SENDER_EMAIL', '')
        self.sender_password = sender_password or getattr(config, 'SENDER_PASSWORD', '')
    
    def send_price_alert(self, symbol: str, current_price: float, 
                        threshold: float, alert_type: str, recipient_email: str):
        """
        Send price threshold alert
        alert_type: 'above' or 'below'
        """
        subject = f"Price Alert: {symbol} reached {alert_type} threshold"
        body = f"""
        Stock Price Alert
        
        Symbol: {symbol}
        Current Price: ${current_price:.2f}
        Threshold: ${threshold:.2f}
        Alert Type: Price moved {alert_type} threshold
        
        Action Required: Check your portfolio and consider your next steps.
        """
        
        self._send_email(recipient_email, subject, body)
    
    def send_volume_spike_alert(self, symbol: str, current_volume: int, 
                               average_volume: int, recipient_email: str):
        """Send volume spike alert"""
        spike_ratio = current_volume / average_volume
        subject = f"Volume Alert: {symbol} - Unusual Trading Volume"
        body = f"""
        Unusual Volume Alert
        
        Symbol: {symbol}
        Current Volume: {current_volume:,}
        Average Volume: {average_volume:,}
        Volume Ratio: {spike_ratio:.2f}x
        
        This stock experienced unusual trading volume today.
        """
        
        self._send_email(recipient_email, subject, body)
    
    def send_technical_alert(self, symbol: str, indicator: str, 
                            value: float, signal: str, recipient_email: str):
        """
        Send technical indicator alert
        signal: 'oversold', 'overbought', 'crossover', etc.
        """
        subject = f"Technical Alert: {symbol} - {indicator} {signal}"
        body = f"""
        Technical Indicator Alert
        
        Symbol: {symbol}
        Indicator: {indicator}
        Value: {value:.2f}
        Signal: {signal}
        
        A technical signal has been triggered. Review the chart for confirmation.
        """
        
        self._send_email(recipient_email, subject, body)
    
    def send_bulk_alerts(self, alerts: List[dict]):
        """
        Send multiple alerts
        alerts: List of alert dictionaries with keys: symbol, message, recipient
        """
        for alert in alerts:
            self.send_price_alert(
                symbol=alert['symbol'],
                current_price=alert['current_price'],
                threshold=alert['threshold'],
                alert_type=alert['alert_type'],
                recipient_email=alert['recipient']
            )
    
    def _send_email(self, recipient_email: str, subject: str, body: str):
        """
        Internal method to send email
        """
        try:
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = recipient_email
            message["Subject"] = subject
            
            message.attach(MIMEText(body, "plain"))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            
            text = message.as_string()
            server.sendmail(self.sender_email, recipient_email, text)
            server.quit()
            
            print(f"Email sent successfully to {recipient_email}")
            
        except Exception as e:
            print(f"Failed to send email: {e}")
            raise
