"use client"

import { useState } from "react"
import type { User } from "../App"
import Sidebar from "../components/Sidebar"
import CommandeImport from "../components/CommandeImport"
import CommandeList from "../components/CommandeList"
import RouteOptimization from "../components/RouteOptimization"
import "./Dashboard.css"

interface ManagerDashboardProps {
  user: User
}

export default function ManagerDashboard({ user }: ManagerDashboardProps) {
  const [activeTab, setActiveTab] = useState<"commandes" | "itineraires" | "livreurs">("commandes")
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  const triggerRefresh = () => setRefreshTrigger((prev) => prev + 1)

  return (
    <div className="dashboard">
      <Sidebar user={user} activeTab={activeTab} setActiveTab={setActiveTab} role="gestionnaire" />

      <main className="dashboard-content">
        <div className="container">
          <div className="page-header">
            <h1>Tableau de Bord Gestionnaire</h1>
            <button className="primary" onClick={() => (window.location.href = "/")}>
              Déconnexion
            </button>
          </div>

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
