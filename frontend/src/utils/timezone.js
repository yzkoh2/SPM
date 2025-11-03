/**
 * Converts a datetime-local string (YYYY-MM-DDTHH:mm) from the user's local timezone to UTC
 * @param {string} dateTimeLocalString - DateTime string from datetime-local input (e.g., "2025-11-03T16:00")
 * @returns {string} ISO string in UTC format (e.g., "2025-11-03T08:00:00.000Z")
 */
export function convertLocalToUTC(dateTimeLocalString) {
  if (!dateTimeLocalString) return null

  // Create a Date object from the datetime-local string
  // The browser interprets this as local time
  const localDate = new Date(dateTimeLocalString)

  // Convert to ISO string (UTC)
  return localDate.toISOString()
}

/**
 * Converts a UTC datetime string to a datetime-local format (YYYY-MM-DDTHH:mm) in the user's timezone
 * @param {string} utcDateTimeString - UTC datetime string (e.g., "2025-11-03T08:00:00.000Z")
 * @returns {string} DateTime-local formatted string (e.g., "2025-11-03T16:00")
 */
export function convertUTCToLocal(utcDateTimeString) {
  if (!utcDateTimeString) return ''

  const date = new Date(utcDateTimeString)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')

  return `${year}-${month}-${day}T${hours}:${minutes}`
}

/**
 * Gets the user's timezone
 * @returns {string} User's timezone (e.g., "Asia/Singapore")
 */
export function getUserTimezone() {
  return Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC'
}
