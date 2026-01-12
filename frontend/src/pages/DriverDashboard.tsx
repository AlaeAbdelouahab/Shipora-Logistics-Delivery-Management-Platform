"use client"

import { useState, useEffect } from "react"
import type { User } from "../App"
import "./Dashboard.css"
import axios from "axios"

const API_URL = "http://localhost:8000/api"

interface DriverDashboardProps {
  user: User
}

interface Delivery {
  id: number
  commande_id: number
  statut: string
  ordre_visite: number
  date_planifiee: string
}

export default function DriverDashboard({ user }: DriverDashboardProps) {
  const [deliveries, setDeliveries] = useState<Delivery[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    fetchDeliveries()
  }, [])

  const fetchDeliveries = async () => {
    try {
      const config = {
        headers: { Authorization: `Bearer ${user.token}` },
      }
      const response = await axios.get(`${API_URL}/livraisons/`, config)
      setDeliveries(response.data)
    } catch (err) {
      setError("Erreur lors du chargement des livraisons")
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const updateStatus = async (livraisonId: number, newStatus: string) => {
    try {
      const config = {
        headers: { Authorization: `Bearer ${user.token}` },
      }
      await axios.put(
        `${API_URL}/livraisons/${livraisonId}`,
        {
          statut: newStatus,
        },
        config,
      )
      fetchDeliveries()
    } catch (err) {
      setError("Erreur lors de la mise à jour")
      console.error(err)
    }
  }

  return (
    <div className="dashboard">
      <main className="dashboard-content" style={{ marginLeft: 0 }}>
        <div className="container">
          <div className="page-header">
            <h1>Mes Livraisons du Jour</h1>
            <button
              className="secondary"
              onClick={() => {
                localStorage.removeItem("user")
                window.location.href = "/login"
              }}
            >
              Déconnexion
            </button>
          </div>

          {error && <div className="error">{error}</div>}

          {loading ? (
            <div style={{ textAlign: "center", padding: "40px" }}>Chargement...</div>
          ) : (
            <div className="card">
              <table>
                <thead>
                  <tr>
                    <th>Ordre</th>
                    <th>Commande ID</th>
                    <th>Adresse</th>
                    <th>Statut</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {deliveries.length === 0 ? (
                    <tr>
                      <td colSpan={5} style={{ textAlign: "center" }}>
                        Aucune livraison pour aujourd'hui
                      </td>
                    </tr>
                  ) : (
                    deliveries.map((delivery) => (
                      <tr key={delivery.id}>
                        <td>{delivery.ordre_visite || "-"}</td>
                        <td>{delivery.commande_id}</td>
                        <td>Adresse</td>
                        <td>
                          <span className={`badge badge-${delivery.statut.toLowerCase()}`}>{delivery.statut}</span>
                        </td>
                        <td>
                          <button
                            className="primary"
                            onClick={() => updateStatus(delivery.id, "livree")}
                            style={{ fontSize: "12px", padding: "6px 10px" }}
                          >
                            Marquer comme livré
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
