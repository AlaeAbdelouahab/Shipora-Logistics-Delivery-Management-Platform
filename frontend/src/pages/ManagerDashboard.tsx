import { useState, useEffect } from "react"
import axios from "axios"
import type { User } from "../App"
import Sidebar from "../components/Sidebar"
import CommandeImport from "../components/CommandeImport"
import CommandeList from "../components/CommandeList"
import RouteOptimization from "../components/RouteOptimization"
import DashboardStats from "../components/DashboardStats"
import "./Dashboard.css"
import "../styles/global.css"
import "./ManagerDashboard.css"

const API_URL = "http://localhost:8000/api"

interface ManagerStats {
  total_commandes: number
  commandes_livrees: number
  commandes_en_attente: number
  livreurs_actifs: number
  distance_moyenne: number
  taux_occupation: number
}

interface ManagerDashboardProps {
  user: User
}

export default function ManagerDashboard({ user }: ManagerDashboardProps) {
  const [activeTab, setActiveTab] = useState<"dashboard" | "commandes" | "itineraires" | "livreurs">("dashboard")
  const [refreshTrigger, setRefreshTrigger] = useState(0)
  const [stats, setStats] = useState<ManagerStats | null>(null)

  const triggerRefresh = () => setRefreshTrigger((prev) => prev + 1)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const config = {
        headers: { Authorization: `Bearer ${user.token}` },
      }
      const response = await axios.get(`${API_URL}/reports/manager-stats?depot_id=${user.depot_id}`, config)
      setStats(response.data)
    } catch (err) {
      console.error("Erreur lors de la récupération des stats", err)
    }
  }

  return (
    <div className="dashboard">
      <Sidebar user={user} activeTab={activeTab} setActiveTab={setActiveTab} role="gestionnaire" />

      <main className="dashboard-content">
        <div className="container">
          <div className="page-header">
            <div className="page-title-section">
              <h1>Tableau de Bord</h1>
              <p className="depot-info">Dépôt ID: {user.depot_id}</p>
            </div>
            <button className="btn btn-primary" onClick={() => (window.location.href = "/")}>
              Déconnexion
            </button>
          </div>

          {activeTab === "dashboard" && (
            <>
              <DashboardStats user={user} />
              {stats && (
                <div className="manager-stats-section">
                  <div className="stats-row">
                    <div className="stat-box">
                      <h4>Distance Moyenne</h4>
                      <p className="stat-number">{stats.distance_moyenne.toFixed(1)} km</p>
                    </div>
                    <div className="stat-box">
                      <h4>Taux d'Occupation</h4>
                      <p className="stat-number">{stats.taux_occupation.toFixed(0)}%</p>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}

          {activeTab === "commandes" && (
            <>
              <CommandeImport user={user} onImportSuccess={triggerRefresh} />
              <CommandeList user={user} refreshTrigger={refreshTrigger} />
            </>
          )}

          {activeTab === "itineraires" && <RouteOptimization user={user} />}

          {activeTab === "livreurs" && (
            <div className="card">
              <h2>Gestion des Livreurs</h2>
              <p>Gestion des livreurs en construction...</p>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
