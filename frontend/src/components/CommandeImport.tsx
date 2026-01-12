"use client"

import type React from "react"

import { useState } from "react"
import axios from "axios"
import type { User } from "../App"

const API_URL = "http://localhost:8000/api"

interface CommandeImportProps {
  user: User
  onImportSuccess: () => void
}

export default function CommandeImport({ user, onImportSuccess }: CommandeImportProps) {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState("")

  const handleImport = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) return

    setLoading(true)
    setMessage("")

    try {
      const formData = new FormData()
      formData.append("file", file)
      formData.append("depot_id", user.depot_id.toString())

      const config = {
        headers: {
          Authorization: `Bearer ${user.token}`,
          "Content-Type": "multipart/form-data",
        },
      }

      const response = await axios.post(`${API_URL}/commandes/import_excel`, formData, config)
      setMessage(`Succès: ${response.data.imported} commandes importées`)
      setFile(null)
      onImportSuccess()
    } catch (err: any) {
      setMessage(`Erreur: ${err.response?.data?.detail || "Erreur inconnue"}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h2>Importer des commandes (Excel)</h2>

      {message && <div className={message.includes("Succès") ? "success" : "error"}>{message}</div>}

      <form onSubmit={handleImport} style={{ maxWidth: "500px" }}>
        <div className="form-group">
          <label>Fichier Excel (colonnes: id_commande, adresse, poids)</label>
          <input type="file" accept=".xlsx,.xls" onChange={(e) => setFile(e.target.files?.[0] || null)} required />
        </div>

        <button type="submit" className="primary" disabled={loading || !file}>
          {loading ? "Import en cours..." : "Importer"}
        </button>
      </form>
    </div>
  )
}
