import Link from 'next/link'
import { ArrowRight } from 'lucide-react'
import Image from 'next/image'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-white">
      <nav className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <Image 
                src="/logos/cuseai-logo.png" 
                alt="CuseAI Logo" 
                width={120} 
                height={40}
                className="h-10 w-auto"
              />
            </div>
            <div className="flex gap-6 items-center">
              <Link href="/demo" className="text-gray-600 hover:text-orange-600 font-medium transition-colors">
                Demo
              </Link>
              <Link href="/contact" className="text-gray-600 hover:text-orange-600 font-medium transition-colors">
                Contact
              </Link>
              <Link href="/dashboard" className="bg-gradient-to-r from-orange-600 to-orange-500 text-white px-6 py-2.5 rounded-lg hover:shadow-lg hover:scale-105 transition-all duration-200 font-semibold">
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center space-y-8">
          <h1 className="text-6xl font-bold leading-tight bg-gradient-to-r from-orange-600 to-orange-500 bg-clip-text text-transparent">
            AI Shopping Assistant Built by SU Students for<br/>
            Local Businesses
          </h1>
          
          <p className="text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
            Turn your website visitors into customers with AI-powered product search. 
            Help shoppers find exactly what they're looking for in seconds, not minutes.
          </p>

          <div className="flex gap-6 justify-center flex-wrap">
            <Link 
              href="/dashboard"
              className="inline-flex items-center gap-3 bg-gradient-to-r from-orange-600 to-orange-500 text-white px-10 py-5 rounded-xl text-lg font-bold hover:shadow-2xl hover:scale-105 transition-all duration-200"
            >
              Get Started Free 
              <ArrowRight className="w-6 h-6" />
            </Link>
            <Link 
              href="/demo" 
              className="border-2 border-gray-300 bg-white px-8 py-4 rounded-xl text-lg font-semibold hover:border-orange-500 hover:shadow-lg transition-all duration-200"
            >
              See Live Demo
            </Link>
          </div>

          <p className="text-sm text-gray-500">
            🎉 <strong>Special Offer:</strong> First 10 Syracuse businesses get 60 days FREE
          </p>
        </div>

        <div className="mt-20 grid md:grid-cols-3 gap-8">
          <div className="bg-white p-8 rounded-2xl shadow-lg hover:shadow-2xl transition-shadow">
            <div className="text-5xl mb-4">⚡</div>
            <h3 className="text-2xl font-bold mb-3 text-gray-900">5-Minute Setup</h3>
            <p className="text-gray-600 leading-relaxed">
              Add one line of code to your website. No technical knowledge required. We handle everything.
            </p>
          </div>

          <div className="bg-white p-8 rounded-2xl shadow-lg hover:shadow-2xl transition-shadow">
            <div className="text-5xl mb-4">🤖</div>
            <h3 className="text-2xl font-bold mb-3 text-gray-900">Smart AI Assistant</h3>
            <p className="text-gray-600 leading-relaxed">
              Answers questions about products, prices, sizes, colors, and stock availability instantly.
            </p>
          </div>

          <div className="bg-white p-8 rounded-2xl shadow-lg hover:shadow-2xl transition-shadow">
            <div className="text-5xl mb-4">🍊</div>
            <h3 className="text-2xl font-bold mb-3 text-gray-900">Local SU Support</h3>
            <p className="text-gray-600 leading-relaxed">
              Built by Syracuse University students. Get help from people who care about local businesses.
            </p>
          </div>
        </div>

        <div className="mt-20 bg-gradient-to-r from-orange-600 to-orange-500 rounded-3xl p-12 text-center text-white">
          <h2 className="text-4xl font-bold mb-4">Ready to help your customers?</h2>
          <p className="text-xl mb-8 opacity-90">Join Syracuse businesses using AI to boost sales</p>
          <Link 
            href="/dashboard"
            className="inline-block bg-white text-orange-600 px-10 py-4 rounded-xl text-lg font-bold hover:shadow-2xl hover:scale-105 transition-all"
          >
            Get Started
          </Link>
        </div>
      </div>
    </div>
  )
}
