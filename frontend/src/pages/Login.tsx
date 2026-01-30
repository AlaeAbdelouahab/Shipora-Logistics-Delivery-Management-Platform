import type React from "react"

import { useState } from "react"
import { useNavigate } from "react-router-dom"
import axios from "axios"
import "./Login.css"

const API_URL = "http://localhost:8000/api"

interface LoginProps {
  setUser: (user: any) => void
}

export default function Login({ setUser }: LoginProps) {
  const navigate = useNavigate()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)

    try {
      const response = await axios.post(`${API_URL}/auth/login`, {
        email,
        mot_de_passe: password,
      })

      const userData = {
        user_id: response.data.user_id,
        role: response.data.role,
        depot_id: response.data.depot_id,
        token: response.data.access_token,
      }

      localStorage.setItem("user", JSON.stringify(userData))
      setUser(userData)

      // Redirect based on role
      const redirects: Record<string, string> = {
        admin: "/admin",
        gestionnaire: "/manager",
        livreur: "/driver",
        client: "/tracking",
      }
      navigate(redirects[userData.role])
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erreur de connexion")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>Système de Gestion Logistique</h1>
        <p className="subtitle">Optimisation des itinéraires de livraison</p>

        {error && <div className="error">{error}</div>}

        <form onSubmit={handleLogin}>
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="votre@email.com"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Mot de passe</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>

          <button type="submit" className="primary" disabled={loading} style={{ width: "100%" }}>
            {loading ? "Connexion en cours..." : "Se connecter"}
          </button>
        </form>

        <div className="demo-accounts">
          <h3>Comptes de démonstration</h3>
          <ul>
            <li>
              <strong>Admin:</strong> admin@example.com
            </li>
            <li>
              <strong>Gestionnaire:</strong> manager@example.com
            </li>
            <li>
              <strong>Livreur:</strong> driver@example.com
            </li>
          </ul>
        </div>
      </div>
    </div>
  )
}
