import { motion, useMotionValue, useTransform, type PanInfo } from 'framer-motion'
import type { Place } from '../types'

const SWIPE_THRESHOLD = 100

interface SwipeCardProps {
  place: Place
  isTop: boolean
  stackIndex: number
  onSwipeLeft: () => void
  onSwipeRight: () => void
}

export default function SwipeCard({ place, isTop, stackIndex, onSwipeLeft, onSwipeRight }: SwipeCardProps) {
  const x = useMotionValue(0)
  const rotate = useTransform(x, [-220, 0, 220], [-18, 0, 18])
  const nopeOpacity = useTransform(x, [-120, -30, 0], [1, 0, 0])
  const yesOpacity = useTransform(x, [0, 30, 120], [0, 0, 1])

  function handleDragEnd(_: unknown, info: PanInfo) {
    if (info.offset.x < -SWIPE_THRESHOLD) {
      onSwipeLeft()
    } else if (info.offset.x > SWIPE_THRESHOLD) {
      onSwipeRight()
    }
  }

  const scale = 1 - stackIndex * 0.04
  const yOffset = stackIndex * 14

  return (
    <motion.div
      className="absolute inset-0 m-auto h-[68vh] max-h-[600px] w-[88vw] max-w-sm cursor-grab overflow-hidden rounded-3xl border-2 border-ink bg-white shadow-hard active:cursor-grabbing"
      style={isTop ? { x, rotate } : undefined}
      initial={false}
      animate={isTop ? { scale: 1, y: 0, opacity: 1 } : { scale, y: yOffset, opacity: stackIndex < 3 ? 1 : 0 }}
      drag={isTop ? 'x' : false}
      dragConstraints={{ left: 0, right: 0 }}
      dragElastic={1}
      onDragEnd={isTop ? handleDragEnd : undefined}
      exit={{
        x: x.get() > 0 ? 400 : -400,
        opacity: 0,
        transition: { duration: 0.25 },
      }}
      whileTap={{ cursor: 'grabbing' }}
    >
      <div className="relative h-[70%] w-full overflow-hidden bg-ink/10">
        {place.image_url ? (
          <img
            src={place.image_url}
            alt={place.name}
            className="h-full w-full object-cover"
            draggable={false}
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center bg-lime">
            <span className="font-display text-4xl font-bold text-ink/40">GoTo</span>
          </div>
        )}

        {isTop && (
          <>
            <motion.div
              style={{ opacity: nopeOpacity }}
              className="absolute left-4 top-4 rotate-[-12deg] rounded-lg border-2 border-coral bg-cream px-3 py-1 font-display text-lg font-bold uppercase text-coral shadow-hard-sm"
            >
              Skip
            </motion.div>
            <motion.div
              style={{ opacity: yesOpacity }}
              className="absolute right-4 top-4 rotate-[12deg] rounded-lg border-2 border-ink bg-lime px-3 py-1 font-display text-lg font-bold uppercase text-ink shadow-hard-sm"
            >
              Details
            </motion.div>
          </>
        )}

        <div className="absolute bottom-0 left-0 rounded-tr-2xl border-r-2 border-t-2 border-ink bg-cream px-3 py-1 font-display text-xs font-semibold uppercase tracking-wide text-ink">
          {place.category}
        </div>
      </div>

      <div className="flex h-[30%] flex-col justify-center gap-1 px-5">
        <h2 className="font-display text-2xl font-bold leading-tight text-ink line-clamp-2">
          {place.name}
        </h2>
        <p className="font-body text-sm text-ink/60 line-clamp-1">
          {place.description}
        </p>
        {place.rating && (
          <div className="mt-1 inline-flex w-fit items-center gap-1 rounded-full border-2 border-ink bg-lime px-2 py-0.5 font-display text-xs font-bold text-ink">
            ★ {place.rating.toFixed(1)}
          </div>
        )}
      </div>
    </motion.div>
  )
}
