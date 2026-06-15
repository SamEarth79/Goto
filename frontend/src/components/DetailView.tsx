import { motion } from 'framer-motion'
import type { Place } from '../types'

interface DetailViewProps {
  place: Place
  onClose: () => void
}

function formatDateTime(iso: string | null): string | null {
  if (!iso) return null
  const date = new Date(iso)
  return date.toLocaleString('en-IN', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    hour: 'numeric',
    minute: '2-digit',
  })
}

export default function DetailView({ place, onClose }: DetailViewProps) {
  const start = formatDateTime(place.start_at)
  const end = formatDateTime(place.end_at)

  return (
    <motion.div
      initial={{ y: '100%' }}
      animate={{ y: 0 }}
      exit={{ y: '100%' }}
      transition={{ type: 'spring', damping: 28, stiffness: 280 }}
      className="fixed inset-0 z-50 flex flex-col overflow-y-auto bg-cream"
    >
      <div className="relative h-72 w-full shrink-0 overflow-hidden bg-ink/10 sm:h-96">
        {place.image_url ? (
          <img src={place.image_url} alt={place.name} className="h-full w-full object-cover" />
        ) : (
          <div className="flex h-full w-full items-center justify-center bg-lime">
            <span className="font-display text-5xl font-bold text-ink/40">GoTo</span>
          </div>
        )}

        <button
          onClick={onClose}
          aria-label="Close"
          className="absolute right-4 top-4 flex h-11 w-11 items-center justify-center rounded-full border-2 border-ink bg-cream font-display text-xl font-bold text-ink shadow-hard-sm active:translate-x-[2px] active:translate-y-[2px] active:shadow-none"
        >
          ✕
        </button>

        <div className="absolute bottom-0 left-0 rounded-tr-2xl border-r-2 border-t-2 border-ink bg-lime px-3 py-1 font-display text-xs font-semibold uppercase tracking-wide text-ink">
          {place.category}
        </div>
      </div>

      <div className="flex flex-1 flex-col gap-4 px-6 py-6 pb-12">
        <div>
          <h1 className="font-display text-3xl font-bold leading-tight text-ink">{place.name}</h1>
          {place.description && (
            <p className="mt-2 font-body text-base text-ink/70">{place.description}</p>
          )}
        </div>

        <div className="flex flex-wrap gap-2">
          {place.rating && (
            <span className="inline-flex items-center gap-1 rounded-full border-2 border-ink bg-lime px-3 py-1 font-display text-sm font-bold text-ink shadow-hard-sm">
              ★ {place.rating.toFixed(1)}
            </span>
          )}
          {place.is_free !== null && (
            <span className="inline-flex items-center gap-1 rounded-full border-2 border-ink bg-cream px-3 py-1 font-display text-sm font-bold text-ink shadow-hard-sm">
              {place.is_free ? 'Free entry' : 'Paid event'}
            </span>
          )}
          {place.kind === 'event' && (
            <span className="inline-flex items-center gap-1 rounded-full border-2 border-ink bg-coral px-3 py-1 font-display text-sm font-bold text-cream shadow-hard-sm">
              Event
            </span>
          )}
        </div>

        {(start || end) && (
          <div className="rounded-2xl border-2 border-ink bg-white px-4 py-3 shadow-hard-sm">
            <p className="font-display text-xs font-semibold uppercase tracking-wide text-ink/50">When</p>
            <p className="mt-1 font-body text-sm font-medium text-ink">
              {start}
              {end ? ` — ${end}` : ''}
            </p>
          </div>
        )}

        {place.address && (
          <div className="rounded-2xl border-2 border-ink bg-white px-4 py-3 shadow-hard-sm">
            <p className="font-display text-xs font-semibold uppercase tracking-wide text-ink/50">Address</p>
            <p className="mt-1 font-body text-sm font-medium text-ink">{place.address}</p>
          </div>
        )}

        {place.hours && (
          <div className="rounded-2xl border-2 border-ink bg-white px-4 py-3 shadow-hard-sm">
            <p className="font-display text-xs font-semibold uppercase tracking-wide text-ink/50">Hours</p>
            <p className="mt-1 font-body text-sm font-medium text-ink">{place.hours}</p>
          </div>
        )}

        {place.source_url && (
          <a
            href={place.source_url}
            target="_blank"
            rel="noreferrer"
            className="mt-2 inline-flex items-center justify-center rounded-2xl border-2 border-ink bg-coral px-6 py-3 font-display text-lg font-bold uppercase tracking-wide text-cream shadow-hard-sm active:translate-x-[2px] active:translate-y-[2px] active:shadow-none"
          >
            {place.kind === 'event' ? 'View on Luma' : 'Open in Maps'}
          </a>
        )}

        <button
          onClick={onClose}
          className="rounded-2xl border-2 border-ink bg-white px-6 py-3 font-display text-lg font-bold uppercase tracking-wide text-ink shadow-hard-sm active:translate-x-[2px] active:translate-y-[2px] active:shadow-none"
        >
          Back to deck
        </button>
      </div>
    </motion.div>
  )
}
