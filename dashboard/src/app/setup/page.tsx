'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'

export default function Setup() {
  const [businessName, setBusinessName] = useState('')
  const [websiteUrl, setWebsiteUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)

    const res = await fetch('/api/setup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ businessName, websiteUrl })
    })

    if (res.ok) {
      router.push('/dashboard')
    } else {
      alert('Error setting up business')
    }
    
    setLoading(false)
  }

  return (
    <div className="max-w-md mx-auto p-8 mt-12">
      <h1 className="text-3xl font-bold mb-8">Set Up Your Business</h1>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">Business Name</label>
          <input
            type="text"
            value={businessName}
            onChange={(e) => setBusinessName(e.target.value)}
            className="w-full p-2 border rounded"
            required
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-2">Website URL</label>
          <input
            type="url"
            value={websiteUrl}
            onChange={(e) => setWebsiteUrl(e.target.value)}
            className="w-full p-2 border rounded"
            placeholder="https://example.com"
            required
          />
        </div>
        
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Setting up...' : 'Create Business'}
        </button>
      </form>
    </div>
  )
}