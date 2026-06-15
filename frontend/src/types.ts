export type PlaceKind = 'place' | 'event'

export interface Place {
  id: string
  kind: PlaceKind
  source: 'cafe' | 'park' | 'brewery' | 'attraction' | 'luma'
  name: string
  category: string
  description: string
  address: string
  rating: number | null
  latitude: number | null
  longitude: number | null
  image_url: string | null
  source_url: string | null
  hours: string | null
  start_at: string | null
  end_at: string | null
  is_free: boolean | null
  score: number
}
