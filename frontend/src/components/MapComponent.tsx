import { useEffect, useRef } from "react"
import "leaflet/dist/leaflet.css"
import L from "leaflet"

interface RoutePoint {
  lat: number
  lon: number
  label: string
  order?: number
}

interface DepotPoint {
  nom: string
  lat: number
  lon: number
}

interface MapComponentProps {
  center?: [number, number]
  zoom?: number
  points?: RoutePoint[]         // commandes
  depot?: DepotPoint | null     // depot
  showRoute?: boolean
  routeColor?: string           // couleur de l’itinéraire
  depotColor?: string           // couleur unique du dépôt
}

// Fix for Leaflet default markers
const DefaultIcon = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
})
L.Marker.prototype.options.icon = DefaultIcon

function coloredDivIcon(color: string) {
  return L.divIcon({
    className: "",
    html: `<div style="
      width: 14px;
      height: 14px;
      background:${color};
      border: 2px solid white;
      border-radius: 50%;
      box-shadow: 0 0 6px rgba(0,0,0,.35);
    "></div>`,
    iconSize: [14, 14],
    iconAnchor: [7, 7],
  })
}

export default function MapComponent({
  center = [48.8566, 2.3522],
  zoom = 10,
  points = [],
  depot = null,
  showRoute = false,
  routeColor = "#3B82F6",
  depotColor = "#F59E0B",
}: MapComponentProps) {
  const mapRef = useRef<L.Map | null>(null)
  const markersRef = useRef<L.Layer[]>([])
  const polylineRef = useRef<L.Polyline | null>(null)

  useEffect(() => {
    if (!mapRef.current) {
      mapRef.current = L.map("map").setView(center, zoom)
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors",
        maxZoom: 19,
      }).addTo(mapRef.current)
    }

    // clear
    markersRef.current.forEach((layer) => (layer as any).remove())
    markersRef.current = []
    if (polylineRef.current) polylineRef.current.remove()

    const coordinates: [number, number][] = []

    // ✅ depot marker (always first)
    if (depot) {
      const depotMarker = L.marker([depot.lat, depot.lon], {
        title: depot.nom,
        icon: coloredDivIcon(depotColor),
      }).bindPopup(`<b>${depot.nom}</b>`)

      depotMarker.addTo(mapRef.current!)
      markersRef.current.push(depotMarker)
      coordinates.push([depot.lat, depot.lon])
    }

    // ✅ commandes markers
    points.forEach((p) => {
      const marker = L.marker([p.lat, p.lon], {
        title: p.label,
        icon: coloredDivIcon(routeColor),
      }).bindPopup(`<b>${p.label}</b>${p.order ? `<div>Ordre: ${p.order}</div>` : ""}`)

      marker.addTo(mapRef.current!)
      markersRef.current.push(marker)
      coordinates.push([p.lat, p.lon])
    })

    // ✅ continuous route line
    if (showRoute && coordinates.length > 1) {
      polylineRef.current = L.polyline(coordinates, {
        color: routeColor,
        weight: 4,
        opacity: 0.85,
        // no dashArray => continuous line
      }).addTo(mapRef.current!)
    }

    // fit bounds
    if (markersRef.current.length) {
      const group = L.featureGroup(markersRef.current as any)
      mapRef.current!.fitBounds(group.getBounds(), { padding: [50, 50] })
    }
  }, [points, depot, center, zoom, showRoute, routeColor, depotColor])

  return (
    <div style={{ width: "100%", height: "400px", borderRadius: "8px", overflow: "hidden" }}>
      <div id="map" style={{ width: "100%", height: "100%" }} />
    </div>
  )
}
