import { auth } from '@clerk/nextjs/server'
import { supabase } from '@/lib/supabase'
import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  const { userId } = await auth()
  
  if (!userId) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const { businessName, websiteUrl } = await request.json()

  // Check if business already exists
  const { data: existing } = await supabase
    .from('businesses')
    .select('*')
    .eq('user_id', userId)
    .single()

  if (existing) {
    return NextResponse.json({ error: 'Business already exists' }, { status: 400 })
  }

  // Create new business
  const { data, error } = await supabase
    .from('businesses')
    .insert({
      user_id: userId,
      business_name: businessName,
      website_url: websiteUrl
    })
    .select()
    .single()

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }

  // Trigger automatic crawl via webhook
  try {
    await fetch('https://web-production-902d.up.railway.app/webhooks/business-created', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        business_id: data.id,
        website_url: websiteUrl
      })
    })
  } catch (e) {
    console.error('Failed to trigger crawl:', e)
  }

  return NextResponse.json(data)
}