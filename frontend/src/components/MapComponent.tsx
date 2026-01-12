"use client"

import { useEffect, useRef } from "react"
import "leaflet/dist/leaflet.css"
import L from "leaflet"

interface RoutePoint {
  lat: number
  lon: number
  label: string
  order?: number
  color?: string
}

interface MapComponentProps {
  center?: [number, number]
  zoom?: number
  routes?: RoutePoint[]
  showRoute?: boolean
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

export default function MapComponent({
  center = [48.8566, 2.3522], // Paris
  zoom = 10,
  routes = [],
  showRoute = false,
}: MapComponentProps) {
  const mapRef = useRef<L.Map | null>(null)
  const markersRef = useRef<L.Marker[]>([])
  const polylineRef = useRef<L.Polyline | null>(null)

  useEffect(() => {
    if (!mapRef.current) {
      // Initialize map
      mapRef.current = L.map("map").setView(center, zoom)
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors",
        maxZoom: 19,
      }).addTo(mapRef.current)
    }

    // Clear existing markers
    markersRef.current.forEach((marker) => marker.remove())
    markersRef.current = []
    if (polylineRef.current) {
      polylineRef.current.remove()
    }

    // Add new markers
    if (routes.length > 0) {
      const coordinates: [number, number][] = []

      routes.forEach((point, index) => {
        const marker = L.marker([point.lat, point.lon], {
          title: point.label,
        })

        const color = point.color || "#3B82F6"
        const popupContent = `
          <div style="font-weight: bold;">${point.label}</div>
          ${point.order ? `<div>Ordre: ${point.order}</div>` : ""}
          <div>Lat: ${point.lat.toFixed(4)}</div>
          <div>Lon: ${point.lon.toFixed(4)}</div>
        `

        marker.bindPopup(popupContent)
        marker.addTo(mapRef.current!)
        markersRef.current.push(marker)

        coordinates.push([point.lat, point.lon])
      })

      // Draw route if requested
      if (showRoute && coordinates.length > 1) {
        polylineRef.current = L.polyline(coordinates, {
          color: "#10B981",
          weight: 3,
          opacity: 0.7,
          dashArray: "5, 5",
        }).addTo(mapRef.current!)
      }

      // Fit bounds to all markers
      if (markersRef.current.length > 0) {
        const group = L.featureGroup(markersRef.current)
        mapRef.current!.fitBounds(group.getBounds(), { padding: [50, 50] })
      }
    }
  }, [routes, center, zoom, showRoute])

  return (
    <div style={{ width: "100%", height: "400px", borderRadius: "8px", overflow: "hidden" }}>
      <div id="map" style={{ width: "100%", height: "100%" }} />
    </div>
  )
}
