interface LandingProps {
  onExplore: (query: string) => void
  loading: boolean
  error: string | null
  query: string
  onQueryChange: (query: string) => void
}

export default function Landing({ onExplore, loading, error, query, onQueryChange }: LandingProps) {
  return (
    <div className="flex h-full min-h-screen flex-col items-center justify-center gap-8 px-6 text-center">
      <div className="flex flex-col items-center">
        <h1 className="font-display text-[5.5rem] font-bold leading-none tracking-tight text-ink sm:text-[7rem]">
          Go<span className="text-coral">-</span>To
        </h1>
        <p className="mt-2 font-display text-lg font-medium uppercase tracking-[0.35em] text-ink/50">
          Bengaluru
        </p>
      </div>

      <div className="rounded-full border-2 border-ink bg-lime px-5 py-2 font-display text-sm font-semibold uppercase tracking-wide text-ink shadow-hard-sm">
        Swipe your way around the city
      </div>

      <input
        type="text"
        value={query}
        onChange={(e) => onQueryChange(e.target.value)}
        placeholder="chill cafe with good coffee"
        className="w-full max-w-sm rounded-2xl border-2 border-ink bg-white px-5 py-3 text-center font-body text-base text-ink placeholder:text-ink/40 shadow-hard-sm focus:outline-none focus:ring-2 focus:ring-coral"
      />

      <button
        onClick={() => onExplore(query)}
        disabled={loading}
        className="mt-4 rounded-2xl border-2 border-ink bg-coral px-12 py-4 font-display text-2xl font-bold uppercase tracking-wide text-cream shadow-hard transition-transform active:translate-x-[3px] active:translate-y-[3px] active:shadow-hard-sm disabled:opacity-60"
      >
        {loading ? 'Finding spots…' : 'Explore'}
      </button>

      {error && (
        <p className="max-w-xs font-body text-sm text-ink/60">{error}</p>
      )}
    </div>
  )
}
