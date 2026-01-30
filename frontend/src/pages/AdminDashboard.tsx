import { useState } from "react"
import type { User } from "../App"
import Sidebar from "../components/Sidebar"
import UserManagement from "../components/UserManagement"
import DashboardStats from "../components/DashboardStats"
import "./Dashboard.css"

interface AdminDashboardProps {
  user: User
}

export default function AdminDashboard({ user }: AdminDashboardProps) {
  const [activeTab, setActiveTab] = useState<"dashboard" | "users" | "reports">("dashboard")

  return (
    <div className="dashboard">
      <Sidebar user={user} activeTab={activeTab} setActiveTab={setActiveTab} role="admin" />

      <main className="dashboard-content">
        <div className="container">
          <div className="page-header">
            <h1>Tableau de Bord Admin</h1>
            <div className="user-info">
              <span>Admin ID: {user.user_id}</span>
            </div>
          </div>

          {activeTab === "dashboard" && <DashboardStats user={user} />}
          {activeTab === "users" && <UserManagement user={user} />}
          {activeTab === "reports" && (
            <div className="card">
              <h2>Rapports</h2>
              <p>Section des rapports en construction...</p>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
