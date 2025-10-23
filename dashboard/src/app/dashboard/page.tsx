import { auth as clerkAuth } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'
import { supabase } from '@/lib/supabase'

export default async function Dashboard() {
  const { userId } = await clerkAuth()
  
  if (!userId) {
    redirect('/')
  }

  // Get business data from Supabase
  const { data: business } = await supabase
    .from('businesses')
    .select('*')
    .eq('user_id', userId)
    .single()

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto p-8">
        <h1 className="text-3xl font-bold mb-8 text-gray-900">Dashboard</h1>
        
        {business ? (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-4 text-gray-900">Your Business</h2>
              <p className="text-gray-800"><strong>Name:</strong> {business.business_name || 'Not set'}</p>
              <p className="text-gray-800"><strong>Website:</strong> {business.website_url || 'Not set'}</p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-4 text-gray-900">Widget Code</h2>
              <p className="text-sm text-gray-600 mb-2">Add this to your website:</p>
              <pre className="bg-gray-100 p-4 rounded overflow-x-auto text-gray-900">
{`<script src="https://your-widget-url.com/widget.js" data-api-key="${business.api_key}"></script>`}
              </pre>
            </div>
          </div>
        ) : (
          redirect('/setup')
        )}
      </div>
    </div>
  )
}
