"use client"

import { useState, useEffect } from "react"
import axios from "axios"
import type { User } from "../App"

const API_URL = "http://localhost:8000/api"

interface Commande {
  id: number
  id_commande: string
  adresse: string
  poids: number
  statut: string
  code_tracking: string
}

interface CommandeListProps {
  user: User
  refreshTrigger: number
}

export default function CommandeList({ user, refreshTrigger }: CommandeListProps) {
  const [commandes, setCommandes] = useState<Commande[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState("all")

  useEffect(() => {
    fetchCommandes()
  }, [refreshTrigger])

  const fetchCommandes = async () => {
    try {
      const config = {
        headers: { Authorization: `Bearer ${user.token}` },
      }
      console.log("Token:", user.token)
      const response = await axios.get(`${API_URL}/commandes/`, config)
      setCommandes(response.data)
    } catch (err) {
      console.error("Erreur lors du chargement des commandes", err)
    } finally {
      setLoading(false)
    }
  }

  const filtered =
    filter === "all" ? commandes : commandes.filter((c) => c.statut.toLowerCase() === filter.toLowerCase())

  return (
    <div className="card">
      <h2>Liste des commandes</h2>

      <div style={{ marginBottom: "20px" }}>
        <select value={filter} onChange={(e) => setFilter(e.target.value)}>
          <option value="all">Tous les statuts</option>
          <option value="en_attente">En attente</option>
          <option value="preparation">Préparation</option>
          <option value="en_transit">En transit</option>
          <option value="livree">Livrée</option>
        </select>
      </div>

      {loading ? (
        <div>Chargement...</div>
      ) : (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Adresse</th>
              <th>Poids (kg)</th>
              <th>Statut</th>
              <th>Code suivi</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={5} style={{ textAlign: "center" }}>
                  Aucune commande
                </td>
              </tr>
            ) : (
              filtered.map((commande) => (
                <tr key={commande.id}>
                  <td>{commande.id_commande}</td>
                  <td>{commande.adresse}</td>
                  <td>{commande.poids}</td>
                  <td>
                    <span className={`badge badge-${commande.statut.toLowerCase()}`}>{commande.statut}</span>
                  </td>
                  <td>{commande.code_tracking}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      )}
    </div>
  )
}
