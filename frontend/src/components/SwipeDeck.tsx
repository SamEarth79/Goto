import { useState } from 'react'
import { AnimatePresence } from 'framer-motion'
import type { Place } from '../types'
import SwipeCard from './SwipeCard'
import DetailView from './DetailView'

interface SwipeDeckProps {
  places: Place[]
  onRestart: () => void
}

export default function SwipeDeck({ places, onRestart }: SwipeDeckProps) {
  const [index, setIndex] = useState(0)
  const [expanded, setExpanded] = useState<Place | null>(null)

  const visible = places.slice(index, index + 3)

  function advance() {
    setIndex((i) => i + 1)
  }

  function handleSwipeRight(place: Place) {
    setExpanded(place)
  }

  function handleDetailClose() {
    setExpanded(null)
    advance()
  }

  return (
    <div className="relative flex h-full min-h-screen flex-col items-center justify-center overflow-hidden px-4 py-6">
      <div className="absolute left-0 right-0 top-0 flex items-center justify-between px-6 pt-4">
        <h1 className="font-display text-xl font-bold tracking-tight text-ink">
          Go<span className="text-coral">-</span>To
        </h1>
        <span className="font-display text-xs font-semibold uppercase tracking-[0.25em] text-ink/40">
          Bengaluru
        </span>
      </div>

      <div className="relative h-[68vh] max-h-[600px] w-[88vw] max-w-sm">
        <AnimatePresence>
          {visible.length > 0 ? (
            visible
              .map((place, i) => (
                <SwipeCard
                  key={place.id}
                  place={place}
                  isTop={i === 0}
                  stackIndex={i}
                  onSwipeLeft={advance}
                  onSwipeRight={() => handleSwipeRight(place)}
                />
              ))
              .reverse()
          ) : (
            <div className="absolute inset-0 m-auto flex h-full w-full flex-col items-center justify-center gap-4 rounded-3xl border-2 border-ink bg-white px-8 text-center shadow-hard">
              <p className="font-display text-2xl font-bold text-ink">That's everything!</p>
              <p className="font-body text-sm text-ink/60">
                You've swiped through today's picks. Start over to see them again.
              </p>
              <button
                onClick={() => {
                  setIndex(0)
                  onRestart()
                }}
                className="mt-2 rounded-2xl border-2 border-ink bg-coral px-6 py-3 font-display text-lg font-bold uppercase tracking-wide text-cream shadow-hard-sm active:translate-x-[2px] active:translate-y-[2px] active:shadow-none"
              >
                Restart
              </button>
            </div>
          )}
        </AnimatePresence>
      </div>

      <div className="mt-6 flex items-center gap-8">
        <div className="flex h-14 w-14 items-center justify-center rounded-full border-2 border-ink bg-cream font-display text-2xl font-bold text-coral shadow-hard-sm">
          ✕
        </div>
        <p className="font-body text-xs text-ink/50">
          Swipe <span className="font-semibold text-coral">left</span> to skip ·{' '}
          <span className="font-semibold text-ink">right</span> for details
        </p>
        <div className="flex h-14 w-14 items-center justify-center rounded-full border-2 border-ink bg-lime font-display text-2xl font-bold text-ink shadow-hard-sm">
          ★
        </div>
      </div>

      <AnimatePresence>
        {expanded && <DetailView place={expanded} onClose={handleDetailClose} />}
      </AnimatePresence>
    </div>
  )
}
