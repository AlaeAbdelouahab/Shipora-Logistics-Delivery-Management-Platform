

import { useState, useEffect } from "react"
import axios from "axios"
import type { User } from "../App"
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts"
import "./DashboardStats.css"

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
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const config = {
        headers: { Authorization: `Bearer ${user.token}` },
      }
      const response = await axios.get(`${API_URL}/reports/dashboard-stats`, config)
      setStats(response.data)
    } catch (err) {
      console.error("Erreur lors de la récupération des stats", err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="loading-spinner">Chargement...</div>
  if (!stats) return <div className="error-message">Erreur lors du chargement</div>

  // Mock data for charts
  const chartData = [
    { name: "Lun", livraisons: stats.total_commandes * 0.2, livrees: stats.commandes_livrees * 0.25 },
    { name: "Mar", livraisons: stats.total_commandes * 0.25, livrees: stats.commandes_livrees * 0.3 },
    { name: "Mer", livraisons: stats.total_commandes * 0.22, livrees: stats.commandes_livrees * 0.28 },
    { name: "Jeu", livraisons: stats.total_commandes * 0.28, livrees: stats.commandes_livrees * 0.35 },
    { name: "Ven", livraisons: stats.total_commandes * 0.25, livrees: stats.commandes_livrees * 0.32 },
  ]

  const pieData = [
    { name: "Livrees", value: stats.commandes_livrees },
    { name: "En attente", value: stats.commandes_en_attente },
  ]

  const COLORS = ["#e3e323", "#262541"]

  return (
    <div className="dashboard-stats-container">
      {/* KPI Cards */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-header">
            <h4>Commandes Totales</h4>
            <span className="kpi-icon">📦</span>
          </div>
          <p className="kpi-value">{stats.total_commandes}</p>
        </div>

        <div className="kpi-card">
          <div className="kpi-header">
            <h4>Livraisons Complétées</h4>
            <span className="kpi-icon">✓</span>
          </div>
          <p className="kpi-value">{stats.commandes_livrees}</p>
        </div>

        <div className="kpi-card">
          <div className="kpi-header">
            <h4>En Attente</h4>
            <span className="kpi-icon">⏳</span>
          </div>
          <p className="kpi-value">{stats.commandes_en_attente}</p>
        </div>

        <div className="kpi-card">
          <div className="kpi-header">
            <h4>Livreurs Actifs</h4>
            <span className="kpi-icon">👥</span>
          </div>
          <p className="kpi-value">{stats.livreurs_actifs}</p>
        </div>
      </div>

      {/* Charts Section */}
      <div className="charts-grid">
        <div className="chart-card">
          <h3>Tendance des Livraisons</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a3a4a" />
              <XAxis dataKey="name" stroke="#00350e" />
              <YAxis stroke="#00350e" />
              <Tooltip contentStyle={{ backgroundColor: "#1a2a3a", border: "1px solid #2a3a4a" }} />
              <Legend />
              <Line type="monotone" dataKey="livraisons" stroke="#e3e323" strokeWidth={2} />
              <Line type="monotone" dataKey="livrees" stroke="#262541" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3>Statut des Commandes</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={pieData} cx="50%" cy="50%" labelLine={false} label={({ name, value }) => `${name}: ${value}`} outerRadius={80} fill="#8884d8" dataKey="value">
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ backgroundColor: "#1a2a3a", border: "1px solid #2a3a4a" }} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card full-width">
          <h3>Performance des Livreurs</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a3a4a" />
              <XAxis dataKey="name" stroke="#a0b0c0" />
              <YAxis stroke="#a0b0c0" />
              <Tooltip contentStyle={{ backgroundColor: "#1a2a3a", border: "1px solid #2a3a4a" }} />
              <Legend />
              <Bar dataKey="livraisons" fill="#262541" />
              <Bar dataKey="livrees" fill="#e3e323" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
