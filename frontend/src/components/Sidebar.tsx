"use client"

import "./Sidebar.css"

interface SidebarProps {
  user: any
  activeTab: string
  setActiveTab: (tab: any) => void
  role: "admin" | "gestionnaire"
}

export default function Sidebar({ role, activeTab, setActiveTab }: SidebarProps) {
  const tabs = role === "admin" ? ["dashboard", "users", "reports"] : ["commandes", "itineraires", "livreurs"]

  const labels: Record<string, string> = {
    dashboard: "Tableau de bord",
    users: "Gestion utilisateurs",
    reports: "Rapports",
    commandes: "Commandes",
    itineraires: "Itinéraires",
    livreurs: "Livreurs",
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2>Logistique</h2>
      </div>

      <nav className="sidebar-nav">
        {tabs.map((tab) => (
          <button
            key={tab}
            className={`nav-item ${activeTab === tab ? "active" : ""}`}
            onClick={() => setActiveTab(tab)}
          >
            {labels[tab]}
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
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
    </aside>
  )
}
