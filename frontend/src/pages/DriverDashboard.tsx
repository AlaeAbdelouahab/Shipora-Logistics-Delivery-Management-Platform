import { useState, useEffect } from "react"
import type { User } from "../App"
import "./Dashboard.css"
import axios from "axios"
import MapComponent from "../components/MapComponent"

const API_URL = "http://localhost:8000/api"

interface DriverDashboardProps {
  user: User
}

interface Commande {
  commande_id: number
  livraison_id: number  // ✅ AJOUT
  order: number
  lat: number
  lon: number
  adresse: string
  statut: string
  poids: number
  code_tracking: string
}

interface DepotDTO {
  id: number
  nom: string
  lat: number
  lon: number
}

interface ItineraireData {
  id: number
  date_planifiee: string
  distance_m: number
  time_s: number
  commandes_count: number
}

interface Route {
  driver_id: number
  commandes: Commande[]
}

export default function DriverDashboard({ user }: DriverDashboardProps) {
  const [route, setRoute] = useState<Route | null>(null)
  const [itineraire, setItineraire] = useState<ItineraireData | null>(null)
  const [depot, setDepot] = useState<DepotDTO | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    fetchDashboard()
  }, [])

  const fetchDashboard = async () => {
    try {
      const config = { headers: { Authorization: `Bearer ${user.token}` } }
      
      const res = await axios.get(`${API_URL}/itineraires/livreur-itineraire`, config)
      
      if (res.data.route && res.data.itineraire) {
        setRoute(res.data.route)
        setItineraire(res.data.itineraire)
        setDepot(res.data.depot ?? null)
      }
    } catch (err) {
      if (axios.isAxiosError(err)) {
        console.log("Erreur détaillée:", err.response?.data)
      }
      setError("Erreur lors du chargement du dashboard")
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const updateStatus = async (livraisonId: number, newStatus: string) => {  
    try {
      const config = { headers: { Authorization: `Bearer ${user.token}` } }
      
      await axios.put(
        `${API_URL}/livraisons/${livraisonId}`, 
        { statut: newStatus }, 
        config
      )
      
      fetchDashboard() // Rafraîchir
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
            <>
              {/* --- Détails de la route --- */}
              {itineraire && (
                <div className="route-details" style={{ marginBottom: "20px" }}>
                  <div className="detail-row">
                    <span className="label">Distance totale:</span>
                    <span className="value">{(itineraire.distance_m / 1000).toFixed(2)} km</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Temps estimé:</span>
                    <span className="value">{(itineraire.time_s / 3600).toFixed(2)} h</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Nombre de colis:</span>
                    <span className="value">{itineraire.commandes_count}</span>
                  </div>
                </div>
              )}

              {/* --- Map du trajet --- */}
              {route && depot && (
                <div style={{ marginBottom: "20px" }}>
                  <MapComponent
                    depot={depot}
                    points={route.commandes
                      .filter(c => c.lat && c.lon)
                      .map(c => ({
                        lat: c.lat,
                        lon: c.lon,
                        label: `Commande ${c.commande_id}`,
                        order: c.order,
                      }))}
                    showRoute
                  />
                </div>
              )}

              {/* --- Tableau des livraisons --- */}
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
                    {!route || route.commandes.length === 0 ? (
                      <tr>
                        <td colSpan={5} style={{ textAlign: "center" }}>
                          Aucune livraison pour aujourd'hui
                        </td>
                      </tr>
                    ) : (
                      route.commandes
                        .sort((a, b) => a.order - b.order)
                        .map((commande) => (
                          <tr key={commande.commande_id}>
                            <td>{commande.order}</td>
                            <td>{commande.commande_id}</td>
                            <td>{commande.adresse || "Adresse non disponible"}</td>
                            <td>
                              <span className={`badge badge-${(commande.statut || "en_attente").toLowerCase()}`}>
                                {commande.statut || "En attente"}
                              </span>
                            </td>
                            <td>
                              {commande.livraison_id && (  // ✅ Vérifier que livraison_id existe
                                <button
                                  className="primary"
                                  onClick={() => updateStatus(commande.livraison_id, "livree")}  // ✅ CHANGEMENT ICI
                                  style={{ fontSize: "12px", padding: "6px 10px" }}
                                  disabled={commande.statut === "livree"}
                                >
                                  {commande.statut === "livree" ? "Livré ✓" : "Marquer comme livré"}
                                </button>
                              )}
                            </td>
                          </tr>
                        ))
                    )}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  )
}