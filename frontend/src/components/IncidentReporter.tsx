"use client"

import type React from "react"

import { useState } from "react"
import axios from "axios"
import type { User } from "../App"

const API_URL = "http://localhost:8000/api"

interface IncidentReporterProps {
  user: User
  commandeId?: number
  onSuccess?: () => void
}

export default function IncidentReporter({ user, commandeId, onSuccess }: IncidentReporterProps) {
  const [type, setType] = useState("autre")
  const [description, setDescription] = useState("")
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!commandeId) {
      setMessage("Erreur: ID de commande manquant")
      return
    }

    setLoading(true)
    setMessage("")

    try {
      const config = {
        headers: { Authorization: `Bearer ${user.token}` },
      }
      await axios.post(
        `${API_URL}/incidents/`,
        {
          commande_id: commandeId,
          type_incident: type,
          description,
        },
        config,
      )

      setMessage("Incident signalé avec succès")
      setDescription("")
      setType("autre")
      if (onSuccess) {
        onSuccess()
      }
    } catch (err: any) {
      setMessage(`Erreur: ${err.response?.data?.detail || "Erreur inconnue"}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: "400px" }}>
      <div className="form-group">
        <label>Type d'incident</label>
        <select value={type} onChange={(e) => setType(e.target.value)}>
          <option value="adresse_invalide">Adresse invalide</option>
          <option value="client_absent">Client absent</option>
          <option value="refus_livraison">Refus de livraison</option>
          <option value="colis_endommage">Colis endommagé</option>
          <option value="annulation_client">Annulation client</option>
          <option value="autre">Autre</option>
        </select>
      </div>

      <div className="form-group">
        <label>Description</label>
        <textarea value={description} onChange={(e) => setDescription(e.target.value)} required rows={4} />
      </div>

      {message && <div className={message.includes("succès") ? "success" : "error"}>{message}</div>}

      <button type="submit" className="primary" disabled={loading}>
        {loading ? "Envoi..." : "Signaler l'incident"}
      </button>
    </form>
  )
}
