import { Link } from 'react-router-dom'
import { useLanguage } from '../context/LanguageContext.jsx'

export function NotFoundPage() {
  const { t } = useLanguage()

  return (
    <main className="grid min-h-[100dvh] place-items-center px-4 py-10">
      <div className="surface-shell w-full max-w-md">
        <div className="surface-core p-6 text-center">
          <p className="font-mono text-sm text-qabul-muted">404</p>
          <h1 className="mt-2 text-3xl font-black tracking-[-0.055em]">{t('notFound.title')}</h1>
          <p className="mt-2 text-sm leading-6 text-qabul-muted">
            {t('notFound.description')}
          </p>
          <Link className="btn btn-primary mt-5" to="/">
            {t('notFound.back')}
          </Link>
        </div>
      </div>
    </main>
  )
}
