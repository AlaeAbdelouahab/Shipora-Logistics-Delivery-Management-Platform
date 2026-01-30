import { useEffect, useMemo, useState } from "react"
import axios from "axios"
import type { User } from "../App"
import RouteVisualization from "./RouteVisualisation"

const API_URL = "http://localhost:8000/api"

interface RouteCommande {
  commande_id: number
  order: number
  lat: number
  lon: number
}

interface Route {
  driver_id: number
  commandes: RouteCommande[]
  distance_m: number
  time_s: number
  commandes_count: number
}

interface ItineraireHistoryRow {
  id: number
  date_planifiee: string
  depot_id: number
  livreur_id: number
  distance_totale: number
  temps_total: number
  commandes_count: number
  optimise: boolean
  date_creation: string
}

interface DepotDTO {
  id: number
  nom: string
  adresse: string
  lat: number
  lon: number
}

interface ItinerairesResponse {
  target_day?: string
  window?: { start: string; end: string }
  routes: Route[]
  itineraires: ItineraireHistoryRow[]
  depot?: DepotDTO | null
}

interface RouteOptimizationProps {
  user: User
}

export default function RouteOptimization({ user }: RouteOptimizationProps) {
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState("")
  const [data, setData] = useState<ItinerairesResponse | null>(null)

  const config = useMemo(() => ({ headers: { Authorization: `Bearer ${user.token}` } }), [user.token])

  const fetchItineraires = async () => {
    setLoading(true)
    setMessage("")
    try {
      const res = await axios.get(`${API_URL}/itineraires/`, config)
      setData(res.data)

      if (!res.data?.routes?.length) {
        setMessage("Aucun itinéraire trouvé pour la fenêtre opérationnelle (pas de routes à afficher).")
      }
    } catch (err: any) {
      setMessage(`Erreur: ${err.response?.data?.detail || "Erreur inconnue"}`)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchItineraires()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <div className="card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
        <div>
          <h2>Itinéraires</h2>
          {data?.target_day && (
            <p style={{ marginTop: 6, opacity: 0.8 }}>
              Jour opérationnel : <strong>{data.target_day}</strong>
            </p>
          )}
        </div>

        <button className="btn btn-secondary" onClick={fetchItineraires} disabled={loading}>
          {loading ? "Chargement..." : "Rafraîchir"}
        </button>
      </div>

      {message && (
        <div className={message.toLowerCase().includes("erreur") ? "error" : "success"} style={{ marginTop: 12 }}>
          {message}
        </div>
      )}

      <div style={{ marginTop: 20 }}>
        {data?.routes?.length ? (
          <RouteVisualization routes={data.routes} depot={data.depot ?? null} />
        ) : (
          <div style={{ marginTop: 10, opacity: 0.8 }}>
            {loading ? "Chargement de la map..." : "Aucune route à afficher pour le moment."}
          </div>
        )}
      </div>

      <div style={{ marginTop: 28 }}>
        <h3 style={{ marginBottom: 12 }}>Historique (fenêtre actuelle)</h3>
        {data?.itineraires?.length ? <HistoryTable rows={data.itineraires} /> : <div style={{ opacity: 0.8 }}>Aucun itinéraire.</div>}
      </div>
    </div>
  )
}

function HistoryTable({ rows }: { rows: ItineraireHistoryRow[] }) {
  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ textAlign: "left" }}>
            <th style={th}>ID</th>
            <th style={th}>Livreur</th>
            <th style={th}>Date planifiée</th>
            <th style={th}>Distance (km)</th>
            <th style={th}>Temps (min)</th>
            <th style={th}>Colis</th>
            <th style={th}>Optimisé</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((it) => (
            <tr key={it.id}>
              <td style={td}>{it.id}</td>
              <td style={td}>{it.livreur_id}</td>
              <td style={td}>{new Date(it.date_planifiee).toLocaleString()}</td>
              <td style={td}>{(it.distance_totale ?? 0).toFixed(2)}</td>
              <td style={td}>{it.temps_total ?? 0}</td>
              <td style={td}>{it.commandes_count ?? 0}</td>
              <td style={td}>{it.optimise ? "Oui" : "Non"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

const th: React.CSSProperties = {
  padding: "10px 8px",
  borderBottom: "1px solid rgba(0,0,0,0.12)",
  fontWeight: 700,
  fontSize: 13,
}
const td: React.CSSProperties = {
  padding: "10px 8px",
  borderBottom: "1px solid rgba(0,0,0,0.08)",
  fontSize: 13,
}
