export function money(value) {
  const number = Number(value || 0)
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'TJS',
    maximumFractionDigits: number % 1 === 0 ? 0 : 2,
  }).format(number)
}

export function number(value) {
  return new Intl.NumberFormat('ru-RU').format(Number(value || 0))
}

export function formatDateTime(value) {
  if (!value) return ''
  return new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

export function formatDate(value) {
  if (!value) return ''
  return new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: 'short',
  }).format(new Date(value))
}
