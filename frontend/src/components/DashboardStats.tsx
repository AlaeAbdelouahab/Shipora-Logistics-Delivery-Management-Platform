"use client"

import { useState, useEffect } from "react"
import axios from "axios"
import type { User } from "../App"

const API_URL = "http://localhost:8000/api"

interface Stats {
  total_commandes: number
  commandes_livrees: number
  commandes_en_attente: number
  livreurs_actifs: number
  taux_livraison: number
}

interface DashboardStatsProps {
  user: User
}

export default function DashboardStats({ user }: DashboardStatsProps) {
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
  if (user?.token) {
    fetchStats()
  }
}, [user])

  const fetchStats = async () => {
    if (!user?.token) return
    try {
      const config = {
        headers: { Authorization: `Bearer ${user.token}` },
      }
      console.log("AXIOS CONFIG", config)
      const response = await axios.get(`${API_URL}/reports/dashboard-stats`, config)
      setStats(response.data)
    } catch (err) {
      console.error("Erreur lors de la récupération des stats", err)
    } finally {
      setLoading(false)
      console.log("TOKEN >>>", user.token)
    }
  }

  if (loading) return <div>Chargement...</div>
  if (!stats) return <div>Erreur lors du chargement</div>

  return (
    <div className="stats-grid">
      <div className="stat-card">
        <h3>Commandes Totales</h3>
        <p className="stat-value">{stats.total_commandes}</p>
      </div>
      <div className="stat-card">
        <h3>Commandes Livrées</h3>
        <p className="stat-value" style={{ color: "var(--secondary)" }}>
          {stats.commandes_livrees}
        </p>
      </div>
      <div className="stat-card">
        <h3>En Attente</h3>
        <p className="stat-value" style={{ color: "var(--warning)" }}>
          {stats.commandes_en_attente}
        </p>
      </div>
      <div className="stat-card">
        <h3>Livreurs Actifs</h3>
        <p className="stat-value" style={{ color: "var(--primary)" }}>
          {stats.livreurs_actifs}
        </p>
      </div>
      <div className="stat-card">
        <h3>Taux de Livraison</h3>
        <p className="stat-value">{stats.taux_livraison.toFixed(1)}%</p>
      </div>
    </div>
  )
}

const styles = `
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stat-card h3 {
  font-size: 14px;
  color: var(--gray-600);
  margin-bottom: 12px;
  text-transform: uppercase;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--gray-900);
}
`
