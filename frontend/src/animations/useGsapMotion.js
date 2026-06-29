import { useGSAP } from '@gsap/react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(useGSAP, ScrollTrigger)

export function useGsapMotion(scope, deps = []) {
  useGSAP(
    () => {
      const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
      if (reduceMotion) return

      gsap.set('[data-gsap="fade-up"]', { autoAlpha: 0, y: 22 })
      gsap.set('[data-gsap="card"]', {
        autoAlpha: 0,
        y: 26,
        rotateX: 4,
        transformPerspective: 900,
      })

      gsap.to('[data-gsap="fade-up"]', {
        autoAlpha: 1,
        y: 0,
        duration: 0.72,
        stagger: 0.07,
        ease: 'power3.out',
      })

      gsap.to('[data-gsap="card"]', {
        autoAlpha: 1,
        y: 0,
        rotateX: 0,
        duration: 0.78,
        stagger: 0.075,
        ease: 'power3.out',
      })

      gsap.utils.toArray('[data-scroll-reveal]').forEach((element) => {
        gsap.fromTo(
          element,
          { autoAlpha: 0, y: 34, scale: 0.985 },
          {
            autoAlpha: 1,
            y: 0,
            scale: 1,
            duration: 0.76,
            ease: 'power3.out',
            scrollTrigger: {
              trigger: element,
              start: 'top 88%',
              once: true,
            },
          },
        )
      })

      gsap.utils.toArray('tbody tr').forEach((element, index) => {
        gsap.fromTo(
          element,
          { autoAlpha: 0, x: -12 },
          {
            autoAlpha: 1,
            x: 0,
            duration: 0.48,
            delay: Math.min(index * 0.018, 0.18),
            ease: 'power2.out',
            scrollTrigger: {
              trigger: element,
              start: 'top 95%',
              once: true,
            },
          },
        )
      })

      ScrollTrigger.refresh()
    },
    { scope, dependencies: deps, revertOnUpdate: true },
  )
}
