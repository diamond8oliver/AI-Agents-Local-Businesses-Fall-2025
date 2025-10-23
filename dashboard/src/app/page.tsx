import Link from 'next/link'
import { ArrowRight } from 'lucide-react'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-white">
      <nav className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold bg-gradient-to-r from-orange-600 to-orange-500 bg-clip-text text-transparent">
                CuseAI
              </span>
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
          <h1 className="text-6xl font-bold leading-tight">
            AI Shopping Assistant for<br/>
            Local Businesses
          </h1>
          
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Help your customers find products instantly with AI-powered search. 
            Built by Syracuse University students for Syracuse businesses.
          </p>

          <div className="flex gap-4 justify-center">
            <Link 
              href="/dashboard"
              className="inline-flex items-center gap-2 bg-gradient-to-r from-orange-600 to-orange-500 text-white px-10 py-5 rounded-xl text-lg font-bold hover:shadow-2xl hover:scale-105 transition-all duration-200"
            >
              Get Started Free 
              <ArrowRight className="w-6 h-6" />
            </Link>
            <Link 
              href="/demo"
              className="inline-flex items-center gap-2 bg-white text-orange-600 px-10 py-5 rounded-xl text-lg font-bold border-2 border-orange-600 hover:bg-orange-50 hover:scale-105 transition-all duration-200"
            >
              See Live Demo
            </Link>
          </div>
        </div>

        <div className="mt-20 grid md:grid-cols-3 gap-8">
          <div className="bg-white p-8 rounded-2xl shadow-lg">
            <div className="text-4xl mb-4">🚀</div>
            <h3 className="text-xl font-bold mb-2">5-Minute Setup</h3>
            <p className="text-gray-600">
              Just add one line of code to your website. No technical knowledge required.
            </p>
          </div>

          <div className="bg-white p-8 rounded-2xl shadow-lg">
            <div className="text-4xl mb-4">🤖</div>
            <h3 className="text-xl font-bold mb-2">Smart AI Assistant</h3>
            <p className="text-gray-600">
              Answers customer questions about products, prices, and availability 24/7.
            </p>
          </div>

          <div className="bg-white p-8 rounded-2xl shadow-lg">
            <div className="text-4xl mb-4">🍊</div>
            <h3 className="text-xl font-bold mb-2">Local Support</h3>
            <p className="text-gray-600">
              Built by SU students. Get help from people who know Syracuse businesses.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
