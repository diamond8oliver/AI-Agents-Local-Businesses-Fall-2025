import Link from 'next/link'
import { ArrowRight, Zap, TrendingUp, Shield } from 'lucide-react'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Navigation */}
      <nav className="border-b bg-white/80 backdrop-blur-sm fixed w-full z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="text-2xl font-bold text-orange-600">CuseAI</div>
            <div className="flex gap-4">
              <Link href="/demo" className="text-gray-600 hover:text-gray-900">
                Demo
              </Link>
              <Link href="/sign-in" className="bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700">
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            AI Shopping Assistant for<br/>
            <span className="text-orange-600">Syracuse Businesses</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Help your customers find products instantly with AI. Like having your best salesperson available 24/7.
          </p>
          <div className="flex gap-4 justify-center">
            <Link href="/sign-in" className="bg-orange-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-orange-700 flex items-center gap-2">
              Get Free Setup <ArrowRight className="w-5 h-5" />
            </Link>
            <Link href="/demo" className="border-2 border-gray-300 px-8 py-4 rounded-lg text-lg font-semibold hover:border-gray-400">
              See Demo
            </Link>
          </div>
          <p className="mt-6 text-sm text-gray-500">
            🎓 Built by Syracuse University students • First 10 businesses get 60 days FREE
          </p>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">Why Syracuse Businesses Choose Us</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard 
              icon={<Zap className="w-8 h-8 text-orange-600" />}
              title="5-Minute Setup"
              description="We install and configure everything for you. No coding required."
            />
            <FeatureCard 
              icon={<TrendingUp className="w-8 h-8 text-orange-600" />}
              title="Daily Auto-Updates"
              description="Your products sync automatically every night. Always up to date."
            />
            <FeatureCard 
              icon={<Shield className="w-8 h-8 text-orange-600" />}
              title="Local Support"
              description="We're here in Syracuse. In-person help when you need it."
            />
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>
          <div className="grid md:grid-cols-4 gap-8">
            <Step number="1" title="We Crawl Your Site" description="Our AI learns your products in 5 minutes" />
            <Step number="2" title="Widget Goes Live" description="Add one line of code to your website" />
            <Step number="3" title="Customers Chat" description="They ask questions in natural language" />
            <Step number="4" title="AI Responds" description="Instant product recommendations with links" />
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">Simple Pricing</h2>
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <PricingCard 
              name="Free"
              price="$0"
              features={["50 products", "100 conversations/mo", "Basic support"]}
            />
            <PricingCard 
              name="Starter"
              price="$49"
              features={["500 products", "1,000 conversations/mo", "Priority support", "Custom branding"]}
              highlighted
            />
            <PricingCard 
              name="Pro"
              price="$99"
              features={["5,000 products", "10,000 conversations/mo", "24/7 support", "Advanced analytics"]}
            />
          </div>
          <p className="text-center mt-8 text-orange-600 font-semibold">
            🎉 First 10 Syracuse businesses get 60 days FREE on any plan
          </p>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto text-center px-4">
          <h2 className="text-4xl font-bold mb-6">Ready to Help Your Customers Find What They Need?</h2>
          <p className="text-xl text-gray-600 mb-8">
            Join Syracuse businesses using AI to increase sales and improve customer experience.
          </p>
          <Link href="/sign-in" className="bg-orange-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-orange-700 inline-flex items-center gap-2">
            Get Started Free <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-12 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 text-center text-gray-600">
          <p className="mb-2">🍊 Proudly built at Syracuse University</p>
          <p>Supporting the Syracuse business community</p>
        </div>
      </footer>
    </div>
  )
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
      <div className="mb-4">{icon}</div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  )
}

function Step({ number, title, description }: { number: string, title: string, description: string }) {
  return (
    <div className="text-center">
      <div className="w-12 h-12 bg-orange-600 text-white rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-4">
        {number}
      </div>
      <h3 className="font-semibold mb-2">{title}</h3>
      <p className="text-sm text-gray-600">{description}</p>
    </div>
  )
}

function PricingCard({ name, price, features, highlighted = false }: { name: string, price: string, features: string[], highlighted?: boolean }) {
  return (
    <div className={`bg-white p-8 rounded-xl ${highlighted ? 'ring-2 ring-orange-600 shadow-lg' : 'border border-gray-200'}`}>
      {highlighted && <div className="text-orange-600 text-sm font-semibold mb-2">MOST POPULAR</div>}
      <h3 className="text-2xl font-bold mb-2">{name}</h3>
      <div className="mb-6">
        <span className="text-4xl font-bold">{price}</span>
        <span className="text-gray-600">/month</span>
      </div>
      <ul className="space-y-3 mb-8">
        {features.map((feature, i) => (
          <li key={i} className="flex items-center gap-2">
            <div className="w-5 h-5 bg-green-100 rounded-full flex items-center justify-center">
              <span className="text-green-600 text-sm">✓</span>
            </div>
            <span className="text-gray-700">{feature}</span>
          </li>
        ))}
      </ul>
      <Link href="/sign-in" className={`block text-center py-3 rounded-lg font-semibold ${highlighted ? 'bg-orange-600 text-white hover:bg-orange-700' : 'border-2 border-gray-300 hover:border-gray-400'}`}>
        Get Started
      </Link>
    </div>
  )
}
