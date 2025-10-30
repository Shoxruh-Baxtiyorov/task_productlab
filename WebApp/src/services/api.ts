import { 
  FreelancerType, 
  SegmentListItem, 
  SegmentResponse, 
  AllFreelancers,
  Task
} from '../types'
import { API_BASE_URL, MIN_USERS_THRESHOLD } from '../constants'
import { getAvatarUrl } from '../utils/avatar'
import { formatDistance, parseISO, format } from 'date-fns'
import { ru } from 'date-fns/locale'

// Получаем все сегменты с количеством пользователей
export async function fetchSegments(): Promise<SegmentListItem[]> {
  const response = await fetch(`${API_BASE_URL}/segments`)
  if (!response.ok) {
    console.error('Failed to fetch segments:', response.status)
    return []
  }
  return response.json()
}

// Получаем фрилансеров по конкретному сегменту и типу
export async function fetchFreelancersBySegment(
  segment: string,
  freelancerType: FreelancerType
): Promise<SegmentResponse[]> {
  if (!segment) {
    return []
  }

  try {
    const response = await fetch(
      `${API_BASE_URL}/segments/freelancer_type_segments/${segment}?freelancer_type=${freelancerType}`
    )

    if (!response.ok) {
      console.error(`Error fetching ${freelancerType} freelancers for ${segment}:`, response.status)
      return []
    }

    return response.json()
  } catch (error) {
    console.error(`Error fetching ${freelancerType} freelancers for ${segment}:`, error)
    return []
  }
}

export function convertApiResponseToExecutor(response: SegmentResponse) {
  const paymentTypes = response.user.payment_types || []
  const paymentTypeLabels: { [key: string]: string } = {
    'CRYPTO': '₿',         // Биткоин символ для криптовалюты
    'NONCASH': '💳',       // Карта для безналичного
    'SELF_EMPLOYED': '📑',  // Документ для самозанятого
    'SBER': '🏦'           // Банк для Сбера
  }

  const formatLocation = (country: string | null) => {
    if (!country) return 'Не указано'
    return country === 'NOTRUSSIA' ? 'Не РФ' : 'РФ'
  }

  const formatRegistrationDate = (date: string | null) => {
    if (!date) return 'Недавно'
    try {
      const parsedDate = parseISO(date)
      return format(parsedDate, 'd MMM yyyy', { locale: ru })
        .replace('.', '')
    } catch (error) {
      console.error('Error formatting date:', error)
      return 'Недавно'
    }
  }

  const calculateDaysRegistered = (date: string | null) => {
    if (!date) return 'Недавно'
    try {
      const parsedDate = parseISO(date)
      return formatDistance(parsedDate, new Date(), { 
        locale: ru,
        addSuffix: true 
      })
      .replace('около ', '')
      .replace(' назад', '')
    } catch (error) {
      console.error('Error calculating days:', error)
      return 'Недавно'
    }
  }

  return {
    name: response.user.full_name,
    role: response.user.prof_level || 'Не указано',
    location: formatLocation(response.user.country),
    rating: response.user.rating || 0,
    registrationDate: formatRegistrationDate(response.user.registered_at),
    originalRegistrationDate: response.user.registered_at || '',
    daysRegistered: calculateDaysRegistered(response.user.registered_at),
    tags: response.user.skills || [],
    stats: {
      reviews: 0,
      contracts: response.segment.claimed_tasks,
      completedTasks: response.segment.completed_tasks
    },
    paymentType: paymentTypes.length > 0 
      ? paymentTypes.map(type => paymentTypeLabels[type] || type).join(' ') 
      : 'Не указано',
    avatar: response.user.avatar || getAvatarUrl(response.user.full_name, response.user.avatar),
    username: response.user.username
  }
}

// Добавим новый тип для событий загрузки
export type LoadingCallback = (
  segment: string, 
  type: FreelancerType, 
  data: SegmentResponse[]
) => void

export async function fetchAllFreelancers(
  onPartialLoad?: LoadingCallback
): Promise<AllFreelancers> {
  try {
    const segments = await fetchSegments()
    const popularSegments = segments.filter(segment => segment.users >= MIN_USERS_THRESHOLD)
    const allFreelancers: AllFreelancers = {}

    const segmentPromises = popularSegments.map(async (segment) => {
      const types: FreelancerType[] = ['WANT', 'WILL', 'IN']
      allFreelancers[segment.name] = {
        WANT: [],
        WILL: [],
        IN: []
      }

      const typePromises = types.map(async (type) => {
        const data = await fetchFreelancersBySegment(segment.name, type)
        // Уведомляем о загрузке части данных
        if (onPartialLoad) {
          onPartialLoad(segment.name, type, data)
        }
        return { type, data }
      })

      const results = await Promise.all(typePromises)
      
      return {
        segment: segment.name,
        data: results.reduce((acc, { type, data }) => {
          acc[type] = data
          return acc
        }, {} as Record<FreelancerType, SegmentResponse[]>)
      }
    })

    const results = await Promise.all(segmentPromises)
    results.forEach(({ segment, data }) => {
      allFreelancers[segment] = data
    })

    return allFreelancers
  } catch (error) {
    console.error('Error fetching all freelancers:', error)
    return {}
  }
}

// Загрузка данных для конкретного сегмента (при поиске)
export async function fetchSegmentData(segment: string) {
  try {
    const types: FreelancerType[] = ['WANT', 'WILL', 'IN']
    const result: { [key in FreelancerType]: SegmentResponse[] } = {
      WANT: [],
      WILL: [],
      IN: []
    }

    // Загружаем данные для каждого типа
    await Promise.all(
      types.map(async (type) => {
        const response = await fetch(
          `${API_BASE_URL}/segments/freelancer_type_segments/${segment}?freelancer_type=${type}`
        )

        if (response.ok) {
          result[type] = await response.json()
        } else {
          console.error(`Error fetching ${type} freelancers for ${segment}:`, response.status)
        }
      })
    )

    return result
  } catch (error) {
    console.error(`Error fetching data for segment ${segment}:`, error)
    return null
  }
}

export async function fetchAvailableTasks(): Promise<Task[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/tasks/freelancer/available`)
    
    if (!response.ok) {
      console.error('Failed to fetch available tasks:', response.status)
      return []
    }

    return response.json()
  } catch (error) {
    console.error('Error fetching available tasks:', error)
    return []
  }
}

interface CheckRegistrationResponse {
  is_registered: boolean
}

// Добавляем функцию проверки регистрации
export async function checkUserRegistration(telegramId: number): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/users/check/${telegramId}`)
    if (!response.ok) {
      return false
    }
    const data: CheckRegistrationResponse = await response.json()
    return data.is_registered
  } catch (error) {
    console.error('Failed to check registration:', error)
    return false
  }
} 