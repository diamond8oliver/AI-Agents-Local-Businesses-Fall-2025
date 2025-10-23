import Link from 'next/link'
import { ArrowRight, Zap, TrendingUp, Shield, CheckCircle2, Sparkles } from 'lucide-react'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="border-b bg-white/80 backdrop-blur-md fixed w-full z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <span className="text-2xl font-bold bg-gradient-to-r from-orange-600 to-orange-500 bg-clip-text text-transparent">
                CuseAI
              </span>
            </div>
            <div className="flex gap-6 items-center">
              <Link href="/demo" className="text-gray-600 hover:text-orange-600 font-medium transition-colors">
                Demo
              </Link>
              <Link href="/dashboard" className="bg-gradient-to-r from-orange-600 to-orange-500 text-white px-6 py-2.5 rounded-lg hover:shadow-lg hover:scale-105 transition-all duration-200 font-semibold">
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 relative overflow-hidden">
        {/* Background decoration */}
        <div className="absolute inset-0 bg-gradient-to-br from-orange-50 via-white to-blue-50 opacity-50" />
        <div className="absolute top-20 right-20 w-72 h-72 bg-orange-200 rounded-full blur-3xl opacity-20" />
        <div className="absolute bottom-20 left-20 w-96 h-96 bg-blue-200 rounded-full blur-3xl opacity-20" />
        
        <div className="max-w-7xl mx-auto text-center relative z-10">
          <div className="inline-flex items-center gap-2 bg-orange-100 text-orange-700 px-4 py-2 rounded-full text-sm font-semibold mb-8 animate-fade-in">
            <Sparkles className="w-4 h-4" />
            <span>First 10 Syracuse businesses get 60 days FREE</span>
          </div>
          
          <h1 className="text-6xl md:text-7xl font-bold text-gray-900 mb-6 leading-tight">
            AI Shopping Assistant for<br/>
            <span className="bg-gradient-to-r from-orange-600 via-orange-500 to-orange-400 bg-clip-text text-transparent">
              Syracuse Businesses
            </span>
          </h1>
          
          <p className="text-xl md:text-2xl text-gray-600 mb-10 max-w-3xl mx-auto leading-relaxed">
            Help your customers find products instantly with AI. Like having your best salesperson available <span className="font-semibold text-gray-900">24/7</span>.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <Link 
              href="/dashboard" 
              className="group bg-gradient-to-r from-orange-600 to-orange-500 text-white px-8 py-4 rounded-xl text-lg font-semibold hover:shadow-2xl hover:scale-105 transition-all duration-200 flex items-center justify-center gap-2"
            >
              Get Free Setup 
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link 
              href="/demo" 
              className="border-2 border-gray-300 bg-white px-8 py-4 rounded-xl text-lg font-semibold hover:border-orange-500 hover:shadow-lg transition-all duration-200"
            >
              See Live Demo
            </Link>
          </div>
          
          <div className="flex items-center justify-center gap-8 text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-green-500" />
              <span>5-min setup</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-green-500" />
              <span>No coding required</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-green-500" />
              <span>Local support</span>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-gradient-to-b from-gray-50 to-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Why Syracuse Businesses Choose Us
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Built by SU students, for local businesses
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard 
              icon={<Zap className="w-10 h-10" />}
              title="5-Minute Setup"
              description="We install and configure everything for you. No coding required."
              gradient="from-yellow-500 to-orange-500"
            />
            <FeatureCard 
              icon={<TrendingUp className="w-10 h-10" />}
              title="Daily Auto-Updates"
              description="Your products sync automatically every night. Always up to date."
              gradient="from-orange-500 to-red-500"
            />
            <FeatureCard 
              icon={<Shield className="w-10 h-10" />}
              title="Local Support"
              description="We're here in Syracuse. In-person help when you need it."
              gradient="from-blue-500 to-indigo-500"
            />
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-4xl md:text-5xl font-bold text-center mb-16">How It Works</h2>
          <div className="grid md:grid-cols-4 gap-8">
            <Step 
              number="1" 
              title="We Crawl Your Site" 
              description="Our AI learns your products in 5 minutes"
              color="bg-orange-500"
            />
            <Step 
              number="2" 
              title="Widget Goes Live" 
              description="Add one line of code to your website"
              color="bg-orange-500"
            />
            <Step 
              number="3" 
              title="Customers Chat" 
              description="They ask questions in natural language"
              color="bg-orange-500"
            />
            <Step 
              number="4" 
              title="AI Responds" 
              description="Instant product recommendations with links"
              color="bg-orange-500"
            />
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="py-24 bg-gradient-to-b from-gray-50 to-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">Simple Pricing</h2>
            <p className="text-xl text-gray-600">Choose the plan that fits your business</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            <PricingCard 
              name="Free"
              price="$0"
              features={["50 products", "100 conversations/mo", "Basic support", "Email support"]}
            />
            <PricingCard 
              name="Starter"
              price="$49"
              features={["500 products", "1,000 conversations/mo", "Priority support", "Custom branding", "Analytics dashboard"]}
              highlighted
            />
            <PricingCard 
              name="Pro"
              price="$99"
              features={["5,000 products", "10,000 conversations/mo", "24/7 support", "Advanced analytics", "Custom integrations"]}
            />
          </div>
          
          <div className="mt-12 text-center">
            <div className="inline-flex items-center gap-2 bg-gradient-to-r from-orange-100 to-orange-50 border-2 border-orange-200 text-orange-700 px-6 py-3 rounded-full font-semibold">
              <Sparkles className="w-5 h-5" />
              <span>🎉 First 10 Syracuse businesses get 60 days FREE on any plan</span>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-br from-orange-600 via-orange-500 to-orange-400 text-white relative overflow-hidden">
        <div className="absolute inset-0 bg-grid-white/10" />
        <div className="max-w-4xl mx-auto text-center px-4 relative z-10">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Ready to Help Your Customers Find What They Need?
          </h2>
          <p className="text-xl md:text-2xl mb-10 text-orange-50">
            Join Syracuse businesses using AI to increase sales and improve customer experience.
          </p>
          <Link 
            href="/dashboard" 
            className="inline-flex items-center gap-2 bg-white text-orange-600 px-10 py-5 rounded-xl text-lg font-bold hover:shadow-2xl hover:scale-105 transition-all duration-200"
          >
            Get Started Free 
            <ArrowRight className="w-6 h-6" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-12 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 text-center text-gray-600">
          <div className="mb-4 text-4xl">🍊</div>
          <p className="mb-2 font-semibold text-gray-900">Proudly built at Syracuse University</p>
          <p>Supporting the Syracuse business community</p>
        </div>
      </footer>
    </div>
  )
}

function FeatureCard({ icon, title, description, gradient }: { 
  icon: React.ReactNode
  title: string
  description: string
  gradient: string
}) {
  return (
    <div className="group bg-white p-8 rounded-2xl shadow-sm border border-gray-100 hover:shadow-xl hover:scale-105 transition-all duration-300">
      <div className={`w-16 h-16 bg-gradient-to-br ${gradient} rounded-xl flex items-center justify-center text-white mb-6 group-hover:scale-110 transition-transform duration-300`}>
        {icon}
      </div>
      <h3 className="text-2xl font-bold mb-3 text-gray-900">{title}</h3>
      <p className="text-gray-600 leading-relaxed">{description}</p>
    </div>
  )
}

function Step({ number, title, description, color }: { 
  number: string
  title: string
  description: string
  color: string
}) {
  return (
    <div className="relative text-center group">
      <div className={`w-16 h-16 ${color} text-white rounded-2xl flex items-center justify-center text-2xl font-bold mx-auto mb-6 shadow-lg group-hover:scale-110 transition-transform duration-300`}>
        {number}
      </div>
      <h3 className="text-xl font-bold mb-3 text-gray-900">{title}</h3>
      <p className="text-gray-600 leading-relaxed">{description}</p>
    </div>
  )
}

function PricingCard({ name, price, features, highlighted = false }: { 
  name: string
  price: string
  features: string[]
  highlighted?: boolean
}) {
  return (
    <div className={`relative bg-white p-10 rounded-2xl transition-all duration-300 ${
      highlighted 
        ? 'ring-4 ring-orange-500 shadow-2xl scale-105' 
        : 'border border-gray-200 hover:shadow-xl hover:scale-105'
    }`}>
      {highlighted && (
        <div className="absolute -top-5 left-1/2 -translate-x-1/2">
          <div className="bg-gradient-to-r from-orange-600 to-orange-500 text-white px-6 py-2 rounded-full text-sm font-bold shadow-lg">
            MOST POPULAR
          </div>
        </div>
      )}
      
      <h3 className="text-2xl font-bold mb-2 text-gray-900">{name}</h3>
      <div className="mb-8">
        <span className="text-5xl font-bold text-gray-900">{price}</span>
        <span className="text-gray-600 text-lg">/month</span>
      </div>
      
      <ul className="space-y-4 mb-10">
        {features.map((feature, i) => (
          <li key={i} className="flex items-start gap-3">
            <CheckCircle2 className="w-6 h-6 text-green-500 flex-shrink-0 mt-0.5" />
            <span className="text-gray-700">{feature}</span>
          </li>
        ))}
      </ul>
      
      <Link 
        href="/dashboard" 
        className={`block text-center py-4 rounded-xl font-bold transition-all duration-200 ${
          highlighted 
            ? 'bg-gradient-to-r from-orange-600 to-orange-500 text-white hover:shadow-xl hover:scale-105' 
            : 'border-2 border-gray-300 text-gray-900 hover:border-orange-500 hover:shadow-lg'
        }`}
      >
        Get Started
      </Link>
    </div>
  )
}
