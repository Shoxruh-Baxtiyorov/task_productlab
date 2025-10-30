import { Executor } from '../types'

export type SortType = 'asc' | 'desc' | 'new'

export const sortExecutors = (
  executors: Executor[], 
  sortType: SortType
) => {
  switch (sortType) {
    case 'asc':
      return [...executors].sort((a, b) => a.rating - b.rating)
    case 'desc':
      return [...executors].sort((a, b) => b.rating - a.rating)
    case 'new':
      return [...executors].sort((a, b) => {
        if (!a.originalRegistrationDate) return 1
        if (!b.originalRegistrationDate) return -1
        
        return new Date(b.originalRegistrationDate).getTime() - 
               new Date(a.originalRegistrationDate).getTime()
      })
    default:
      return executors
  }
} 