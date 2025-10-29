export function useCalendarUtils() {
  const convertToLocalTime = (utcTimestamp) => {
    if (!utcTimestamp) return null
    let dateStr = utcTimestamp
    if (!dateStr.includes('Z') && !dateStr.includes('+')) {
      dateStr = dateStr + 'Z'
    }
    return new Date(dateStr)
  }

  const formatTimeOnly = (deadline) => {
    if (!deadline) return ''
    const date = convertToLocalTime(deadline)
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    })
  }

  const formatFullDateTime = (deadline) => {
    if (!deadline) return 'No deadline'
    const date = convertToLocalTime(deadline)
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    })
  }

  const getTaskColorClass = (task) => {
    const now = new Date()
    const deadline = convertToLocalTime(task.deadline)

    if (task.status === 'Completed') {
      return 'bg-green-100 border-l-4 border-green-500 text-green-800'
    } else if (deadline < now) {
      return 'bg-red-100 border-l-4 border-red-500 text-red-800'
    } else if (task.is_owner) {
      return 'bg-indigo-100 border-l-4 border-indigo-500 text-indigo-800'
    } else {
      return 'bg-green-50 border-l-4 border-green-400 text-green-700'
    }
  }

  const getStatusBadgeColor = (status) => {
    const colors = {
      Unassigned: 'bg-gray-100 text-gray-800',
      Ongoing: 'bg-blue-100 text-blue-800',
      'Under Review': 'bg-yellow-100 text-yellow-800',
      Completed: 'bg-green-100 text-green-800',
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const getDeadlineTextColor = (deadline) => {
    if (!deadline) return 'text-gray-600'

    const now = new Date()
    const deadlineDate = convertToLocalTime(deadline)

    if (deadlineDate < now) return 'text-red-600 font-semibold'
    if (deadlineDate.toDateString() === now.toDateString()) return 'text-orange-600 font-semibold'
    return 'text-gray-700'
  }

  return {
    convertToLocalTime,
    formatTimeOnly,
    formatFullDateTime,
    getTaskColorClass,
    getStatusBadgeColor,
    getDeadlineTextColor,
  }
}
