"use client"

import type React from "react"

import { useState } from "react"
import type { User } from "../App"
import axios from "axios"

const API_URL = "http://localhost:8000/api"

interface UserManagementProps {
  user: User
}

export default function UserManagement({ user }: UserManagementProps) {
  const [nom, setNom] = useState("")
  const [prenom, setPrenom] = useState("")
  const [email, setEmail] = useState("")
  const [role, setRole] = useState("gestionnaire")
  const [message, setMessage] = useState("")
  const [loading, setLoading] = useState(false)

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setMessage("")

    try {
      const config = {
        headers: { Authorization: `Bearer ${user.token}` },
      }
      await axios.post(
        `${API_URL}/auth/register`,
        {
          nom,
          prenom,
          email,
          role,
          depot_id: user.depot_id,
        },
        config,
      )

      setMessage("Utilisateur créé avec succès")
      setNom("")
      setPrenom("")
      setEmail("")
    } catch (err: any) {
      setMessage(`Erreur: ${err.response?.data?.detail || "Erreur inconnue"}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h2>Créer un nouvel utilisateur</h2>

      {message && <div className={message.includes("succès") ? "success" : "error"}>{message}</div>}

      <form onSubmit={handleCreateUser} style={{ maxWidth: "500px" }}>
        <div className="form-group">
          <label>Prénom</label>
          <input type="text" value={prenom} onChange={(e) => setPrenom(e.target.value)} required />
        </div>

        <div className="form-group">
          <label>Nom</label>
          <input type="text" value={nom} onChange={(e) => setNom(e.target.value)} required />
        </div>

        <div className="form-group">
          <label>Email</label>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </div>

        <div className="form-group">
          <label>Rôle</label>
          <select value={role} onChange={(e) => setRole(e.target.value)}>
            <option value="gestionnaire">Gestionnaire</option>
            <option value="livreur">Livreur</option>
          </select>
        </div>

        <button type="submit" className="primary" disabled={loading}>
          {loading ? "Création..." : "Créer utilisateur"}
        </button>
      </form>
    </div>
  )
}
