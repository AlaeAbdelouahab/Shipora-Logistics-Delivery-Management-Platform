"""
Automated scheduler for daily route optimization
Runs at 21:00 every day, iterates through depots, and sends notifications
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import asyncio
import logging
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Depot, Commande, User, Livraison, Itineraire, DeliveryStatus, UserRole
from optimization import RouteOptimizer
from notifications import notification_service
import json
import pytz

logger = logging.getLogger(__name__)

TIMEZONE = pytz.timezone("Africa/Casablanca")

class OptimizationScheduler:
    def __init__(self):
        loop = asyncio.get_event_loop()
        self.scheduler = AsyncIOScheduler(
            event_loop=loop,
            timezone=TIMEZONE
        )


    def start(self):
        """Start the scheduler"""

        self.scheduler.add_job(
            self.daily_optimization,
            CronTrigger(hour=21, minute=00, timezone=TIMEZONE),
            id="daily_optimization",
            name="Daily Route Optimization",
            replace_existing=True,
            misfire_grace_time=3600,  # 1h tolerance
            coalesce=True,
            max_instances=1,
        )

        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("✅ Optimization scheduler started - runs daily at 21:00")

        # 🔍 Debug: show next run time
        job = self.scheduler.get_job("daily_optimization")
        if job:
            logger.info(f"⏰ Next optimization run at: {job.next_run_time}")

    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Optimization scheduler stopped")
    
    async def daily_optimization(self):
        """Main optimization function - runs daily"""
        logger.info("🚀 Starting daily route optimization...")

        db = SessionLocal()
        try:
            depots = db.query(Depot).all()

            for depot in depots:
                await self.optimize_depot(db, depot)

            logger.info("✅ Daily optimization completed successfully")

        except Exception as e:
            logger.exception("❌ Error in daily optimization")
        finally:
            db.close()
    
    async def optimize_depot(self, db: Session, depot: Depot):
        """Optimize routes for a specific depot"""
        logger.info(f"Optimizing depot: {depot.nom} (ID: {depot.id})")
        
        try:
            # Get waiting commandes for this depot
            commandes = db.query(Commande).filter(
                Commande.depot_id == depot.id,
                Commande.statut == DeliveryStatus.EN_ATTENTE
            ).all()
            
            if not commandes:
                logger.info(f"No pending orders for depot {depot.nom}")
                return
            
            # Get active drivers for this depot
            drivers = db.query(User).filter(
                User.depot_id == depot.id,
                User.role == UserRole.LIVREUR,
                User.actif == True
            ).all()
            
            if not drivers:
                logger.warning(f"No active drivers for depot {depot.nom}")
                return
            
            # Prepare data for optimizer
            commandes_data = [
                {
                    "id": c.id,
                    "latitude": c.latitude,
                    "longitude": c.longitude,
                    "poids": c.poids,
                    "service_time_minutes": 10,
                    "created_at": c.date_creation.isoformat()
                }
                for c in commandes
            ]
            
            drivers_data = [
                {
                    "id": d.id,
                    "email": d.email,
                    "name": f"{d.prenom} {d.nom}",
                    "capacity_kg": 100  # Default capacity
                }
                for d in drivers
            ]
            
            # Run optimization
            optimizer = RouteOptimizer()
            result = optimizer.optimize(
                commandes=commandes_data,
                drivers=drivers_data,
                depot_coords=(depot.latitude, depot.longitude),
                planning_date=datetime.now().date().isoformat()
            )
            
            if not result.get("routes"):
                logger.warning(f"Optimization returned no routes for depot {depot.nom}")
                return
            
            # Save results to database
            tomorrow = datetime.now().date() + timedelta(days=1)
            planning_date = datetime.combine(tomorrow, datetime.min.time())
            
            scheduled_count = 0
            unscheduled_count = result.get("commandes_unscheduled", 0)
            
            for route in result["routes"]:
                # Create itinerary record
                itineraire = Itineraire(
                    date_planifiee=planning_date,
                    depot_id=depot.id,
                    livreur_id=route["driver_id"],
                    distance_totale=route["distance_m"] / 1000,  # Convert to km
                    temps_total=int(route["time_s"] / 60),  # Convert to minutes
                    commandes_count=route["commandes_count"],
                    optimise=True,
                    metadonnees=json.dumps(route)
                )
                db.add(itineraire)
                
                # Update or create livraisons with optimized sequence
                for commande_info in route["commandes"]:
                    commande = db.query(Commande).filter(
                        Commande.id == commande_info["commande_id"]
                    ).first()
                    
                    if commande:
                        livraison = db.query(Livraison).filter(
                            Livraison.commande_id == commande.id,
                            Livraison.livreur_id == route["driver_id"]
                        ).first()
                        
                        if livraison:
                            livraison.ordre_visite = commande_info["order"]
                            livraison.date_planifiee = planning_date
                        else:
                            livraison = Livraison(
                                commande_id=commande.id,
                                livreur_id=route["driver_id"],
                                date_planifiee=planning_date,
                                ordre_visite=commande_info["order"],
                                statut=DeliveryStatus.PREPARATION
                            )
                            db.add(livraison)
                        
                        commande.statut = DeliveryStatus.PREPARATION
                        scheduled_count += 1
            
            db.commit()
            
            # Send notifications to drivers
            await self.send_driver_notifications(db, result["routes"], planning_date)
            
            # Send summary to depot manager
            await self.send_manager_notification(db, depot, result, planning_date)
            
            logger.info(
                f"Depot {depot.nom}: {scheduled_count} orders scheduled, "
                f"{unscheduled_count} postponed"
            )
        
        except Exception as e:
            db.rollback()
            logger.error(f"Error optimizing depot {depot.nom}: {str(e)}")
    
    async def send_driver_notifications(self, db: Session, routes: list, planning_date):
        """Send itinerary notifications to each driver"""
        for route in routes:
            try:
                driver = db.query(User).filter(User.id == route["driver_id"]).first()
                
                if driver and driver.email:
                    subject = f"Votre itinéraire de livraison - {planning_date.strftime('%d/%m/%Y')}"
                    
                    # Create detailed route summary
                    route_html = "<ul>"
                    for commande in route["commandes"]:
                        route_html += f"<li>Commande {commande['commande_id']} - Arrêt #{commande['order']}</li>"
                    route_html += "</ul>"
                    
                    html_content = f"""
                    <html>
                        <body style="font-family: Arial, sans-serif; color: #333;">
                            <h2>Nouvel Itinéraire Assigné</h2>
                            <p>Bonjour {driver.prenom},</p>
                            <p>Un nouvel itinéraire de livraison vous a été automatiquement assigné.</p>
                            
                            <div style="background: #f0f0f0; padding: 15px; border-radius: 5px; margin: 20px 0;">
                                <p><strong>Date:</strong> {planning_date.strftime('%d/%m/%Y')}</p>
                                <p><strong>Nombre de colis:</strong> {route['commandes_count']}</p>
                                <p><strong>Distance estimée:</strong> {route['distance_m']/1000:.1f} km</p>
                                <p><strong>Temps estimé:</strong> {int(route['time_s']/60)} minutes</p>
                            </div>
                            
                            <h3>Vos arrêts:</h3>
                            {route_html}
                            
                            <p style="margin-top: 30px;">
                                <strong>Consultez votre application</strong> pour voir le détail de votre itinéraire.
                            </p>
                            <p>Merci pour votre engagement!</p>
                            <p style="color: #666; font-size: 12px;">Système de Gestion Logistique</p>
                        </body>
                    </html>
                    """
                    
                    await notification_service.send_email(driver.email, subject, html_content)
                    logger.info(f"Sent itinerary notification to driver {driver.nom}")
            except Exception as e:
                logger.error(f"Error sending driver notification: {str(e)}")
    
    async def send_manager_notification(self, db: Session, depot: Depot, result: dict, planning_date):
        """Send complete optimization summary to depot manager"""
        try:
            manager = db.query(User).filter(
                User.depot_id == depot.id,
                User.role == UserRole.GESTIONNAIRE
            ).first()
            
            if manager and manager.email:
                subject = f"Résumé Optimisation - {depot.nom} - {planning_date.strftime('%d/%m/%Y')}"
                
                # Build routes table
                routes_html = "<table style='border-collapse: collapse; width: 100%;'>"
                routes_html += "<tr style='background: #e9ecef;'><th style='border: 1px solid #ddd; padding: 8px;'>Livreur</th><th style='border: 1px solid #ddd; padding: 8px;'>Colis</th><th style='border: 1px solid #ddd; padding: 8px;'>Distance</th><th style='border: 1px solid #ddd; padding: 8px;'>Temps</th></tr>"
                
                for route in result.get("routes", []):
                    driver = db.query(User).filter(User.id == route["driver_id"]).first()
                    driver_name = f"{driver.prenom} {driver.nom}" if driver else "Unknown"
                    
                    routes_html += f"""
                    <tr>
                        <td style='border: 1px solid #ddd; padding: 8px;'>{driver_name}</td>
                        <td style='border: 1px solid #ddd; padding: 8px;'>{route['commandes_count']}</td>
                        <td style='border: 1px solid #ddd; padding: 8px;'>{route['distance_m']/1000:.1f} km</td>
                        <td style='border: 1px solid #ddd; padding: 8px;'>{int(route['time_s']/60)} min</td>
                    </tr>
                    """
                
                routes_html += "</table>"
                
                html_content = f"""
                <html>
                    <body style="font-family: Arial, sans-serif; color: #333;">
                        <h2>Résumé Optimisation des Routes</h2>
                        <p>Bonjour {manager.prenom},</p>
                        <p>L'optimisation automatique des routes pour le <strong>{planning_date.strftime('%d/%m/%Y')}</strong> est terminée.</p>
                        
                        <div style="background: #d4edda; padding: 15px; border-radius: 5px; border-left: 4px solid #28a745; margin: 20px 0;">
                            <p><strong>Dépôt:</strong> {depot.nom}</p>
                            <p><strong>Commandes planifiées:</strong> {result.get('commandes_scheduled', 0)}</p>
                            <p><strong>Commandes reportées:</strong> {result.get('commandes_unscheduled', 0)}</p>
                            <p><strong>Livreurs engagés:</strong> {result.get('total_vehicles_used', 0)}</p>
                        </div>
                        
                        <h3>Détail des itinéraires:</h3>
                        {routes_html}
                        
                        <div style="margin-top: 30px; padding: 15px; background: #e7f3ff; border-left: 4px solid #0066cc; border-radius: 5px;">
                            <p><strong>Action:</strong> Accédez à votre dashboard pour:</p>
                            <ul>
                                <li>Consulter les itinéraires détaillés</li>
                                <li>Modifier les assignations si nécessaire</li>
                                <li>Voir les commandes reportées</li>
                            </ul>
                        </div>
                        
                        <p style="margin-top: 30px; color: #666; font-size: 12px;">Système de Gestion Logistique</p>
                    </body>
                </html>
                """
                
                await notification_service.send_email(manager.email, subject, html_content)
                logger.info(f"Sent optimization summary to manager {manager.nom}")
        except Exception as e:
            logger.error(f"Error sending manager notification: {str(e)}")

# Global scheduler instance
optimization_scheduler = OptimizationScheduler()
