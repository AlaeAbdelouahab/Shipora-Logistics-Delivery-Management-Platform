"use client"

import { useState } from "react"
import axios from "axios"
import type { User } from "../App"

const API_URL = "http://localhost:8000/api"

interface RouteOptimizationProps {
  user: User
}

export default function RouteOptimization({ user }: RouteOptimizationProps) {
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState("")
  const [optimized, setOptimized] = useState(false)

  const handleOptimize = async () => {
    setLoading(true)
    setMessage("")

    try {
      const config = {
        headers: { Authorization: `Bearer ${user.token}` },
      }

      const response = await axios.post(
        `${API_URL}/itineraires/optimize`,
        {
          depot_id: user.depot_id,
          date_planifiee: new Date().toISOString(),
        },
        config,
      )

      if (response.data.optimized) {
        setMessage("Itinéraires optimisés avec succès!")
        setOptimized(true)
      }
    } catch (err: any) {
      setMessage(`Erreur: ${err.response?.data?.detail || "Erreur inconnue"}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h2>Optimisation des itinéraires</h2>

      <p>
        Cliquez sur le bouton ci-dessous pour optimiser automatiquement les itinéraires de livraison en fonction des
        adresses et des capacités des livreurs.
      </p>

      {message && <div className={message.includes("succès") ? "success" : "error"}>{message}</div>}

      <button className="primary" onClick={handleOptimize} disabled={loading} style={{ marginTop: "20px" }}>
        {loading ? "Optimisation en cours..." : "Optimiser itinéraires"}
      </button>

      {optimized && (
        <div className="success" style={{ marginTop: "20px" }}>
          Les itinéraires ont été générés et envoyés aux livreurs
        </div>
      )}
    </div>
  )
}
