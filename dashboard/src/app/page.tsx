import { auth } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'

export default async function Home() {
  const { userId } = await auth()
  
  if (userId) {
    redirect('/dashboard')
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">Business AI Agent Platform</h1>
        <p className="text-xl text-gray-600 mb-8">Add an AI assistant to your website in minutes</p>
        <p className="text-gray-500">Sign up to get started</p>
      </div>
    </div>
  )
}