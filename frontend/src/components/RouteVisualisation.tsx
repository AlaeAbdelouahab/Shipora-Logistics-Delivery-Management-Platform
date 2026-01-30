import { useMemo, useState } from "react"
import MapComponent from "./MapComponent"
import "./RouteVisualisation.css"

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

interface DepotDTO {
  nom: string
  lat: number
  lon: number
}

const PALETTE = ["#3B82F6", "#10B981", "#a30648", "#EF4444", "#8B5CF6", "#06B6D4"]
const DEPOT_COLOR = "#F59E0B"

function colorForDriver(driverId: number) {
  return PALETTE[driverId % PALETTE.length]
}

export default function RouteVisualization({
  routes,
  depot,
}: {
  routes: Route[]
  depot?: DepotDTO | null
}) {
  const [selectedRoute, setSelectedRoute] = useState(0)

  const currentRoute = routes?.[selectedRoute]
  const routeColor = useMemo(() => (currentRoute ? colorForDriver(currentRoute.driver_id) : "#3B82F6"), [currentRoute])

  if (!routes?.length) return <div className="card">Aucune route à afficher</div>

  const points = currentRoute.commandes
    .slice()
    .sort((a, b) => a.order - b.order)
    .map((c) => ({
      lat: c.lat,
      lon: c.lon,
      label: `Commande ${c.commande_id}`,
      order: c.order,
    }))

  return (
    <div className="route-visualization">
      <div className="route-tabs">
        {routes.map((route, index) => (
          <button
            key={index}
            className={`tab ${selectedRoute === index ? "active" : ""}`}
            onClick={() => setSelectedRoute(index)}
          >
            <span>Livreur {route.driver_id}</span>
            <small>{route.commandes_count} colis</small>
          </button>
        ))}
      </div>

      <div className="route-details">
        <div className="detail-row">
          <span className="label">Distance totale:</span>
          <span className="value">{(currentRoute.distance_m / 1000).toFixed(2)} km</span>
        </div>
        <div className="detail-row">
          <span className="label">Temps estimé:</span>
          <span className="value">{(currentRoute.time_s / 3600).toFixed(2)} h</span>
        </div>
      </div>

      <div className="map-container">
        <MapComponent
          points={points}
          depot={depot ?? null}
          showRoute
          routeColor={routeColor}
          depotColor={DEPOT_COLOR}
        />
      </div>

      <div className="commandes-list">
        <h3>Ordre de visite</h3>
        <ol>
          {currentRoute.commandes
            .slice()
            .sort((a, b) => a.order - b.order)
            .map((commande) => (
              <li key={commande.commande_id}>
                Commande {commande.commande_id} — Ordre {commande.order}
              </li>
            ))}
        </ol>
      </div>
    </div>
  )
}
