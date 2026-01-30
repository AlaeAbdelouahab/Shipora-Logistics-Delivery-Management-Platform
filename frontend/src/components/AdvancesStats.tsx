
import { useState, useEffect } from "react"
import axios from "axios"
import type { User } from "../App"
import "./AdvancedStats.css"

const API_URL = "http://localhost:8000/api"

interface Performance {
  livreur_id: number
  livreur_nom: string
  total: number
  completees: number
  taux: number
}

interface AdvancedStatsProps {
  user: User
}

export default function AdvancedStats({ user }: AdvancedStatsProps) {
  const [performance, setPerformance] = useState<Performance[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchPerformance()
  }, [])

  const fetchPerformance = async () => {
    try {
      const config = {
        headers: { Authorization: `Bearer ${user.token}` },
      }
      const response = await axios.get(`${API_URL}/reports/performance`, config)
      setPerformance(response.data)
    } catch (err) {
      console.error("Erreur lors du chargement des performances", err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div>Chargement...</div>

  return (
    <div className="advanced-stats">
      <h2>Performance des Livreurs</h2>

      {performance.length === 0 ? (
        <p>Aucune donnée disponible</p>
      ) : (
        <div className="performance-grid">
          {performance.map((perf) => (
            <div key={perf.livreur_id} className="performance-card">
              <h3>{perf.livreur_nom}</h3>
              <div className="perf-metric">
                <label>Livraisons</label>
                <span className="metric-value">
                  {perf.completees}/{perf.total}
                </span>
              </div>
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{
                    width: `${perf.taux}%`,
                    backgroundColor: perf.taux >= 90 ? "#10b981" : perf.taux >= 70 ? "#f59e0b" : "#ef4444",
                  }}
                />
              </div>
              <div className="perf-percentage">{perf.taux.toFixed(1)}%</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
