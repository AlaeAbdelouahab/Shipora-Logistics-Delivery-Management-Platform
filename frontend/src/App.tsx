"use client"

import { useState, useEffect } from "react"
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom"
import Landing from "./pages/Landing"
import Login from "./pages/Login"
import AdminDashboard from "./pages/AdminDashboard"
import ManagerDashboard from "./pages/ManagerDashboard"
import DriverDashboard from "./pages/DriverDashboard"
import ClientTracking from "./pages/ClientTracking"
import "./App.css"

export interface User {
  user_id: number
  role: "admin" | "gestionnaire" | "livreur" | "client"
  depot_id: number
  token: string
}

function App() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const storedUser = localStorage.getItem("user")
    if (storedUser) {
      setUser(JSON.parse(storedUser))
    }
    setLoading(false)
  }, [])

  if (loading) {
    return <div className="loading">Chargement...</div>
  }

  return (
    <Router>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login setUser={setUser} />} />
        <Route path="/tracking/:code" element={<ClientTracking />} />

        {/* Protected routes */}
        {user ? (
          <>
            {user.role === "admin" && <Route path="/admin" element={<AdminDashboard user={user} />} />}
            {user.role === "gestionnaire" && <Route path="/manager" element={<ManagerDashboard user={user} />} />}
            {user.role === "livreur" && <Route path="/driver" element={<DriverDashboard user={user} />} />}
            <Route
              path="/dashboard"
              element={
                user.role === "admin" ? (
                  <Navigate to="/admin" />
                ) : user.role === "gestionnaire" ? (
                  <Navigate to="/manager" />
                ) : user.role === "livreur" ? (
                  <Navigate to="/driver" />
                ) : (
                  <Navigate to="/" />
                )
              }
            />
          </>
        ) : null}
      </Routes>
    </Router>
  )
}

export default App
