import type React from "react"

import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { Package, MapPin, Clock, Users, TrendingUp, Heart, Menu, X, ArrowRight, CheckCircle } from "lucide-react"
import "./Landing.css"

export default function Landing() {
  const navigate = useNavigate()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [trackingCode, setTrackingCode] = useState("")
  const [trackingError, setTrackingError] = useState("")

  const handleTrackingSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!trackingCode.trim()) {
      setTrackingError("Veuillez entrer un code de suivi")
      return
    }
    navigate(`/tracking/${trackingCode}`)
  }

  const scrollToSection = (sectionId: string) => {
    setMobileMenuOpen(false)
    const element = document.getElementById(sectionId)
    element?.scrollIntoView({ behavior: "smooth" })
  }

  return (
    <main className="landing-page">
      {/* Navigation */}
      <nav className="navbar">
        <div className="navbar-container">
          <div className="navbar-brand">
            <div className="brand-icon">
              <Package className="w-6 h-6" />
            </div>
            <span className="brand-name">Shipora</span>
          </div>

          {/* Desktop Menu */}
          <div className="navbar-desktop-menu">
            <a href="#features" onClick={() => scrollToSection("features")} className="nav-link">
              Fonctionnalités
            </a>
            <a href="#about" onClick={() => scrollToSection("about")} className="nav-link">
              À propos
            </a>
            <a href="#contact" onClick={() => scrollToSection("contact")} className="nav-link">
              Contact
            </a>
          </div>

          {/* Auth Buttons */}
          <div className="navbar-actions">
            <button onClick={() => navigate("/login")} className="btn-signin">
              Connexion
            </button>
            <button onClick={() => navigate("/login")} className="btn-primary">
              Commencer
            </button>
          </div>

          {/* Mobile Menu Button */}
          <button className="mobile-menu-btn" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="mobile-menu">
            <a href="#features" onClick={() => scrollToSection("features")} className="mobile-nav-link">
              Fonctionnalités
            </a>
            <a href="#about" onClick={() => scrollToSection("about")} className="mobile-nav-link">
              À propos
            </a>
            <a href="#contact" onClick={() => scrollToSection("contact")} className="mobile-nav-link">
              Contact
            </a>
            <button onClick={() => navigate("/login")} className="mobile-btn-primary">
              Se connecter
            </button>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section className="hero">
        <div className="hero-container">
          <div className="hero-content">
            <div className="badge">Plateforme Logistique Intelligente</div>
            <h1 className="hero-title">
              Livraisons Rapides et
              <span className="highlight"> Fiables</span>
            </h1>
            <p className="hero-description">
              Shipora optimise vos itinéraires de livraison, suivi en temps réel, et tient vos clients informés à chaque
              étape.
            </p>
            <div className="hero-buttons">
              <button onClick={() => navigate("/login")} className="btn-primary btn-lg">
                Accéder au Tableau de Bord
                <ArrowRight className="w-4 h-4" />
              </button>
              <button onClick={() => scrollToSection("track")} className="btn-secondary btn-lg">
                Suivre un Colis
              </button>
            </div>
          </div>

          {/* Image en arrière-plan */}
          <div className="hero-image">
            <img src={new URL("../images/image.png", import.meta.url).href} alt="Shipora Delivery" />
          </div>

          <div className="hero-visual">
            <div className="visual-card">
              <div className="stat-item">
                <MapPin className="w-6 h-6 text-white" />
                <div>
                  <p className="stat-label">Routes Optimisées</p>
                  <p className="stat-value">24 Livraisons Aujourd'hui</p>
                </div>
              </div>
              <div className="stat-item">
                <Clock className="w-6 h-6 text-white" />
                <div>
                  <p className="stat-label">Temps Moyen</p>
                  <p className="stat-value">32 minutes par livraison</p>
                </div>
              </div>
              <div className="stat-item">
                <TrendingUp className="w-6 h-6 text-white" />
                <div>
                  <p className="stat-label">Taux de Ponctualité</p>
                  <p className="stat-value">98.5% de Réussite</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Tracking Section */}
      <section id="track" className="tracking-section">
        <div className="section-container">
          <h2>Suivre Votre Colis</h2>
          <p>Entrez votre code de suivi pour voir les mises à jour en temps réel de votre livraison</p>

          <form onSubmit={handleTrackingSubmit} className="tracking-form">
            <div className="form-group">
              <input
                type="text"
                value={trackingCode}
                onChange={(e) => {
                  setTrackingCode(e.target.value)
                  setTrackingError("")
                }}
                placeholder="Ex: SHIP-001"
                className="tracking-input"
              />
              <button type="submit" className="btn-primary">
                Suivre
              </button>
            </div>
            {trackingError && <p className="error-message">{trackingError}</p>}
            <p className="tracking-hint">Codes de démonstration: SHIP-001, SHIP-002, SHIP-003</p>
          </form>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="features-section">
        <div className="section-container">
          <h2>Pourquoi Choisir Shipora?</h2>

          <div className="features-grid">
            {[
              {
                icon: MapPin,
                title: "Optimisation des Routes",
                description:
                  "Algorithmes alimentés par l'IA pour optimiser les routes de livraison et réduire les coûts",
              },
              {
                icon: Clock,
                title: "Suivi en Temps Réel",
                description: "Mises à jour en direct de la collecte à la livraison pour vos clients",
              },
              {
                icon: Package,
                title: "Gestion Complète des Commandes",
                description: "Importez les commandes, gérez l'inventaire et traitez les incidents en un seul endroit",
              },
              {
                icon: Users,
                title: "Support Multi-Rôle",
                description: "Tableaux de bord séparés pour les administrateurs, gestionnaires, livreurs et clients",
              },
              {
                icon: Heart,
                title: "Support 24/7",
                description: "Équipe d'assistance dédiée prête à vous aider avec vos besoins logistiques",
              },
              {
                icon: TrendingUp,
                title: "Analyses Avancées",
                description: "Rapports détaillés sur les performances et la satisfaction des clients",
              },
            ].map((feature, idx) => (
              <div key={idx} className="feature-card">
                <feature.icon className="feature-icon" />
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="about-section">
        <div className="section-container">
          <h2>Solution Logistique Complète</h2>

          <div className="about-grid">
            <div className="about-card">
              <h3>Pour les Clients</h3>
              <ul className="benefits-list">
                {[
                  "Suivi des colis en temps réel avec GPS",
                  "Notifications à chaque étape de la livraison",
                  "Accès à l'historique des livraisons",
                  "Gestion de plusieurs commandes",
                ].map((item, idx) => (
                  <li key={idx}>
                    <CheckCircle className="w-5 h-5" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="about-card">
              <h3>Pour les Entreprises</h3>
              <ul className="benefits-list">
                {[
                  "Import des commandes via Excel avec géocodage automatique",
                  "Optimisation des routes avec algorithme OR-Tools",
                  "Gestion des livreurs et capacités des véhicules",
                  "Suivi des incidents et métriques de qualité",
                ].map((item, idx) => (
                  <li key={idx}>
                    <CheckCircle className="w-5 h-5" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>


      {/* Contact Section */}
      <section id="contact" className="contact-section">
        <div className="section-container contact-content">
          <h2>Nous Contacter</h2>
          <p>Des questions sur Shipora? Notre équipe est prête à vous aider.</p>

          <div className="contact-grid">
            <div className="contact-card">
              <h3>Email</h3>
              <a href="mailto:shipora.team@gmail.com">shipora.team@gmail.com</a>
            </div>
            <div className="contact-card">
              <h3>Téléphone</h3>
              <a href="tel:+212718116731">+212 71811673</a>
            </div>
            <div className="contact-card">
              <h3>Support</h3>
              <a href="mailto:shipora.support@gmail.com">shipora.support@gmail.com</a>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="section-container">
          <div className="footer-content">
            <div className="footer-column">
              <h4>Produit</h4>
              <ul>
                <li>
                  <a href="#features">Fonctionnalités</a>
                </li>
                <li>
                  <a href="#about">À propos</a>
                </li>
                <li>
                  <a href="#contact">Tarification</a>
                </li>
              </ul>
            </div>
            <div className="footer-column">
              <h4>Documentation</h4>
              <ul>
                <li>
                  <a href="#">Docs API</a>
                </li>
                <li>
                  <a href="#">Guides</a>
                </li>
                <li>
                  <a href="#">FAQ</a>
                </li>
              </ul>
            </div>
            <div className="footer-column">
              <h4>Entreprise</h4>
              <ul>
                <li>
                  <a href="#">À propos de nous</a>
                </li>
                <li>
                  <a href="#">Blog</a>
                </li>
                <li>
                  <a href="#">Carrières</a>
                </li>
              </ul>
            </div>
            <div className="footer-column">
              <h4>Légal</h4>
              <ul>
                <li>
                  <a href="#">Confidentialité</a>
                </li>
                <li>
                  <a href="#">Conditions</a>
                </li>
                <li>
                  <a href="#">Contact</a>
                </li>
              </ul>
            </div>
          </div>

          <div className="footer-bottom">
            <p>&copy; 2026 Shipora. Tous droits réservés. Votre partenaire logistique de confiance.</p>
          </div>
        </div>
      </footer>
    </main>
  )
}