
'use client'

import Link from 'next/link'
import { useEffect } from 'react'

export default function DemoPage() {
  useEffect(() => {
    const script = document.createElement('script')
    script.src = 'https://web-production-902d.up.railway.app/widget/widget.js'
    script.setAttribute('data-api-key', '4644670e-936f-4688-87ed-b38d45e3d4e9')
    document.body.appendChild(script)

    return () => {
      if (document.body.contains(script)) {
        document.body.removeChild(script)
      }
    }
  }, [])

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <nav className="border-b bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link href="/" className="text-2xl font-bold text-orange-600">
              CuseAI
            </Link>
            <Link href="/" className="text-gray-900 hover:text-orange-600">
              ← Back to Home
            </Link>
          </div>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold text-center mb-4 text-gray-900">
          Try the AI Assistant
        </h1>
        <p className="text-xl text-gray-700 text-center mb-12">
          Ask about products from Atlas Skateboarding (our demo store)
        </p>

        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-semibold mb-4 text-gray-900">Try These Questions:</h2>
          <ul className="space-y-3">
            <li className="flex items-start gap-3">
              <span className="text-orange-600 font-bold text-xl">•</span>
              <span className="text-gray-800">{`"Show me shoes under $100"`}</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-orange-600 font-bold text-xl">•</span>
              <span className="text-gray-800">{`"What Nike products do you have?"`}</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-orange-600 font-bold text-xl">•</span>
              <span className="text-gray-800">{`"Compare your skateboards"`}</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-orange-600 font-bold text-xl">•</span>
              <span className="text-gray-800">{`"What's in stock right now?"`}</span>
            </li>
          </ul>
        </div>

        <div className="bg-gradient-to-br from-orange-50 to-white rounded-xl p-8 border-2 border-orange-200">
          <p className="text-center text-gray-800 mb-4 font-medium">
            👉 Click the chat bubble in the bottom right to start!
          </p>
          <p className="text-center text-sm text-gray-600">
            This is a live demo using Atlas Skateboarding{`'`}s real product catalog
          </p>
        </div>
      </div>
    </div>
  )
}
