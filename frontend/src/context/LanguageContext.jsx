import { createContext, useContext, useMemo, useState } from 'react'

import { languages, translations } from '../i18n/translations.js'

const LanguageContext = createContext(null)
const defaultLanguage = 'ru'

function readInitialLanguage() {
  const stored = localStorage.getItem('qabul_language')
  return translations[stored] ? stored : defaultLanguage
}

function getPathValue(source, path) {
  return path.split('.').reduce((value, key) => value?.[key], source)
}

export function LanguageProvider({ children }) {
  const [language, setLanguageState] = useState(readInitialLanguage)

  function setLanguage(nextLanguage) {
    if (!translations[nextLanguage]) return
    localStorage.setItem('qabul_language', nextLanguage)
    setLanguageState(nextLanguage)
  }

  function t(path, ...args) {
    const value = getPathValue(translations[language], path) ?? getPathValue(translations[defaultLanguage], path)
    if (typeof value === 'function') return value(...args)
    return value ?? path
  }

  const value = useMemo(
    () => ({ language, languages, setLanguage, t }),
    [language],
  )

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>
}

export function useLanguage() {
  const context = useContext(LanguageContext)
  if (!context) {
    throw new Error('useLanguage must be used inside LanguageProvider')
  }
  return context
}
