'use client'

import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'
import Script from 'next/script'

export default function DemoPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="border-b bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link href="/" className="text-2xl font-bold text-orange-600">
              CuseAI
            </Link>
            <Link href="/" className="text-gray-600 hover:text-orange-600 flex items-center gap-2">
              <ArrowLeft className="w-4 h-4" />
              Back to Home
            </Link>
          </div>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-4 py-16">
        <h1 className="text-4xl font-bold text-center mb-4">Live Demo</h1>
        <p className="text-xl text-gray-600 text-center mb-12">
          Try asking the AI assistant questions about products!
        </p>

        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-bold mb-4">Example Questions to Try:</h2>
          <ul className="space-y-2 text-gray-700">
            <li>• "Show me shoes under $100"</li>
            <li>• "What skateboards do you have?"</li>
            <li>• "Do you have any red products?"</li>
            <li>• "What's in stock right now?"</li>
            <li>• "Show me your bestsellers"</li>
          </ul>
        </div>

        <div className="bg-gradient-to-r from-orange-100 to-orange-50 rounded-xl p-8 text-center">
          <p className="text-lg text-gray-700 mb-4">
            The chat bubble will appear in the bottom right corner 👉
          </p>
          <p className="text-sm text-gray-600">
            This demo uses Atlas Skateboarding's product catalog
          </p>
        </div>
      </div>

      {/* Load the chat widget */}
      <Script
        src="https://web-production-902d.up.railway.app/widget/widget.js"
        data-api-key="4644670e-936f-4688-87ed-b38d45e3d4e9"
        strategy="lazyOnload"
      />
    </div>
  )
}
