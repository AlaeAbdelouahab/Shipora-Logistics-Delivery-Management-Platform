"use client"

import { useState } from "react"
import MapComponent from "./MapComponent"
import type { User } from "../App"
import "./RouteVisualization.css"

interface Route {
  driver_id: number
  commandes: Array<{
    commande_id: number
    order: number
    lat: number
    lon: number
  }>
  distance_m: number
  time_s: number
  commandes_count: number
}

interface RouteVisualizationProps {
  routes: Route[]
  user: User
}

export default function RouteVisualization({ routes, user }: RouteVisualizationProps) {
  const [selectedRoute, setSelectedRoute] = useState<number>(0)

  if (!routes || routes.length === 0) {
    return <div className="card">Aucune route optimisée</div>
  }

  const currentRoute = routes[selectedRoute]
  const mapPoints = currentRoute.commandes.map((c) => ({
    lat: c.lat,
    lon: c.lon,
    label: `Commande ${c.commande_id}`,
    order: c.order,
    color: "#3B82F6",
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
        <MapComponent routes={mapPoints} showRoute={true} />
      </div>

      <div className="commandes-list">
        <h3>Ordre de visite</h3>
        <ol>
          {currentRoute.commandes
            .sort((a, b) => a.order - b.order)
            .map((commande) => (
              <li key={commande.commande_id}>
                Commande {commande.commande_id} - Ordre {commande.order}
              </li>
            ))}
        </ol>
      </div>
    </div>
  )
}
