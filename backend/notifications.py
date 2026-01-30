"""
Notification system for emails and alerts
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
import asyncio

class NotificationService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = os.getenv("SMTP_USER")
        self.sender_password = os.getenv("SMTP_PASSWORD")
    
    async def send_email(self, to_email: str, subject: str, html_content: str):
        """Send email notification"""
        if not self.sender_email or not self.sender_password:
            print(f"Email not configured, skipping: {to_email}")
            return
        
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = to_email
            
            message.attach(MIMEText(html_content, "html"))
            
            # Send in background
            asyncio.create_task(self._send_smtp(to_email, message.as_string()))
        except Exception as e:
            print(f"Error sending email: {e}")
    
    async def _send_smtp(self, to_email: str, message: str):
        """Internal SMTP sending"""
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, to_email, message)
        except Exception as e:
            print(f"SMTP error: {e}")
    
    def get_route_assigned_template(self, driver_name: str, commandes_count: int, date: str) -> str:
        """Email template for route assignment"""
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2>Nouvel Itinéraire Assigné</h2>
                <p>Bonjour {driver_name},</p>
                <p>Un nouvel itinéraire de livraison vous a été assigné pour le <strong>{date}</strong>.</p>
                <div style="background: #f0f0f0; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Nombre de colis:</strong> {commandes_count}</p>
                    <p><strong>Consultez votre application</strong> pour voir l'ordre de visite optimisé.</p>
                </div>
                <p>Merci pour votre engagement!</p>
                <p>Système de Gestion Logistique</p>
            </body>
        </html>
        """
    
    def get_incident_alert_template(self, incident_type: str, commande_id: str) -> str:
        """Email template for incident alerts"""
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2>Alerte Incident</h2>
                <p>Un incident a été signalé :</p>
                <div style="background: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107;">
                    <p><strong>Type:</strong> {incident_type}</p>
                    <p><strong>Commande:</strong> {commande_id}</p>
                    <p><strong>Action Requise:</strong> Consultez le dashboard pour traiter cet incident.</p>
                </div>
            </body>
        </html>
        """

    def get_tracking_code_template(self, id_commande: str, tracking_code: str) -> str:
        """Email template to send tracking code to the client"""
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2>Votre commande a été enregistrée ✅</h2>
                <p>Bonjour,</p>
                <p>Votre commande <strong>{id_commande}</strong> a bien été enregistrée dans notre système.</p>

                <div style="background: #f0f0f0; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0;"><strong>Code de tracking :</strong></p>
                    <p style="font-size: 22px; letter-spacing: 2px; margin: 8px 0;">
                        <strong>{tracking_code}</strong>
                    </p>
                </div>

                <p>Utilisez ce code sur la page de suivi pour connaître l’état de votre livraison.</p>

                <p style="margin-top: 30px; color: #666; font-size: 12px;">
                    Système de Gestion Logistique
                </p>
            </body>
        </html>
        """

# Global notification service
notification_service = NotificationService()
