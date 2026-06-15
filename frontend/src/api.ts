import type { Place } from './types'

export const DEFAULT_QUERY = 'fun things to do, good food and cafes, parks and breweries, events nearby'

export async function fetchPlaces(lat?: number, lng?: number, query: string = DEFAULT_QUERY): Promise<Place[]> {
  const params = new URLSearchParams({ q: query, top: '40' })
  if (lat !== undefined && lng !== undefined) {
    params.set('lat', String(lat))
    params.set('lng', String(lng))
  }
  const res = await fetch(`/api/search?${params.toString()}`)
  if (!res.ok) throw new Error(`Search failed: ${res.status}`)
  return res.json()
}
