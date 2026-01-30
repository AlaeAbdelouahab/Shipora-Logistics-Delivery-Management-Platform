import type React from "react"

import { useState } from "react"
import axios from "axios"
import "./ClientTracking.css"

const API_URL = "http://localhost:8000/api"

interface TrackingInfo {
  code_tracking: string
  statut: string
  adresse: string
  date_creation: string
  livraison: {
    date_planifiee: string
    statut: string
  } | null
}

export default function ClientTracking() {
  const [code, setCode] = useState("")
  const [tracking, setTracking] = useState<TrackingInfo | null>(null)
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const handleTrack = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)

    try {
      const response = await axios.get(`${API_URL}/clients/tracking/${code}`)
      setTracking(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || "Commande non trouvée")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="tracking-container">
      <div className="tracking-card">
        <h1>Suivi de Commande</h1>
        <p>Entrez votre code de suivi pour localiser votre colis</p>

        <form onSubmit={handleTrack}>
          <div className="form-group">
            <input
              type="text"
              value={code}
              onChange={(e) => setCode(e.target.value.toUpperCase())}
              placeholder="Ex: ABC12345"
              required
            />
          </div>
          <button type="submit" className="primary" style={{ width: "100%" }} disabled={loading}>
            {loading ? "Recherche..." : "Suivre ma commande"}
          </button>
        </form>

        {error && <div className="error">{error}</div>}

        {tracking && (
          <div className="tracking-info">
            <h2>Informations de votre commande</h2>
            <div className="info-item">
              <label>Code de suivi:</label>
              <span>{tracking.code_tracking}</span>
            </div>
            <div className="info-item">
              <label>Adresse de livraison:</label>
              <span>{tracking.adresse}</span>
            </div>
            <div className="info-item">
              <label>Statut:</label>
              <span className={`badge badge-${tracking.statut.toLowerCase()}`}>{tracking.statut}</span>
            </div>
            {tracking.livraison && (
              <>
                <div className="info-item">
                  <label>Date planifiée:</label>
                  <span>{new Date(tracking.livraison.date_planifiee).toLocaleDateString("fr-FR")}</span>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
