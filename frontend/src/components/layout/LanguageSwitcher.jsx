import { Globe2 } from 'lucide-react'

import { useLanguage } from '../../context/LanguageContext.jsx'

export function LanguageSwitcher({ compact = false }) {
  const { language, languages, setLanguage, t } = useLanguage()

  return (
    <div className="inline-flex items-center gap-1 rounded-full bg-white p-1 ring-1 ring-qabul-ink/[0.08]">
      <Globe2 size={16} strokeWidth={1.8} className="ml-2 text-qabul-muted" aria-hidden="true" />
      <label className="sr-only" htmlFor={compact ? 'language-select-compact' : 'language-select'}>
        {t('nav.language')}
      </label>
      <select
        id={compact ? 'language-select-compact' : 'language-select'}
        className="h-8 appearance-none bg-transparent pl-1 pr-2 text-xs font-black text-qabul-ink outline-none"
        value={language}
        onChange={(event) => setLanguage(event.target.value)}
        aria-label={t('nav.language')}
      >
        {languages.map((item) => (
          <option key={item.code} value={item.code}>
            {compact ? item.shortLabel : item.label}
          </option>
        ))}
      </select>
    </div>
  )
}
