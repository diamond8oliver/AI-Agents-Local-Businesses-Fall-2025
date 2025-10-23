'use client'

import Link from 'next/link'
import { useState } from 'react'
import { ArrowLeft, Send } from 'lucide-react'

export default function ContactPage() {
  const [submitted, setSubmitted] = useState(false)

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

      <div className="max-w-2xl mx-auto px-4 py-16">
        <h1 className="text-4xl font-bold text-center mb-4">Get in Touch</h1>
        <p className="text-xl text-gray-600 text-center mb-12">
          Interested in adding AI to your business? Let&apos;s talk!
        </p>

        {!submitted ? (
          <form 
            action="https://formspree.io/f/mzzjnbdy" 
            method="POST"
            onSubmit={() => setSubmitted(true)}
            className="bg-white rounded-xl shadow-lg p-8"
          >
            <div className="mb-6">
              <label className="block text-gray-700 font-semibold mb-2">
                Business Name
              </label>
              <input
                type="text"
                name="business"
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                placeholder="Your Business Name"
              />
            </div>

            <div className="mb-6">
              <label className="block text-gray-700 font-semibold mb-2">
                Email Address
              </label>
              <input
                type="email"
                name="email"
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                placeholder="you@yourbusiness.com"
              />
            </div>

            <div className="mb-6">
              <label className="block text-gray-700 font-semibold mb-2">
                Website URL
              </label>
              <input
                type="url"
                name="website"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                placeholder="https://yourbusiness.com"
              />
            </div>

            <div className="mb-6">
              <label className="block text-gray-700 font-semibold mb-2">
                Message (Optional)
              </label>
              <textarea
                rows={4}
                name="message"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                placeholder="Tell us about your business..."
              />
            </div>

            <button
              type="submit"
              className="w-full bg-gradient-to-r from-orange-600 to-orange-500 text-white py-4 rounded-lg font-bold hover:shadow-xl transition-all flex items-center justify-center gap-2"
            >
              Send Message
              <Send className="w-5 h-5" />
            </button>
          </form>
        ) : (
          <div className="bg-green-50 border-2 border-green-200 rounded-xl p-8 text-center">
            <div className="text-6xl mb-4">✅</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Thanks for reaching out!
            </h2>
            <p className="text-gray-600 mb-6">
              We&apos;ll get back to you at aiagentsforsyracuse@gmail.com within 24 hours.
            </p>
            <Link
              href="/"
              className="inline-block bg-orange-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-orange-700"
            >
              Back to Home
            </Link>
          </div>
        )}
      </div>
    </div>
  )
}
