import { useState } from 'react'
import Landing from './components/Landing'
import SwipeDeck from './components/SwipeDeck'
import { fetchPlaces, DEFAULT_QUERY } from './api'
import type { Place } from './types'

function getLocation(): Promise<{ lat?: number; lng?: number }> {
  return new Promise((resolve) => {
    if (!('geolocation' in navigator)) {
      resolve({})
      return
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => resolve({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
      () => resolve({}),
      { timeout: 8000 },
    )
  })
}

export default function App() {
  const [places, setPlaces] = useState<Place[] | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [query, setQuery] = useState('')

  async function handleExplore(searchQuery: string) {
    setLoading(true)
    setError(null)
    try {
      const { lat, lng } = await getLocation()
      const results = await fetchPlaces(lat, lng, searchQuery.trim() || DEFAULT_QUERY)
      setPlaces(results)
    } catch (err) {
      setError('Could not load places. Please try again.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (places) {
    return <SwipeDeck places={places} onRestart={() => setPlaces(null)} />
  }

  return (
    <Landing
      onExplore={handleExplore}
      loading={loading}
      error={error}
      query={query}
      onQueryChange={setQuery}
    />
  )
}
