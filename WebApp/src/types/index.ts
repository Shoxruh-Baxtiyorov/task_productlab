export type FreelancerType = 'WANT' | 'WILL' | 'IN'

export interface Segment {
  id: number
  name: string
  completed_tasks: number
  claimed_tasks: number
}

export interface User {
  id: number
  full_name: string
  bio: string | null
  skills: string[] | null
  prof_level: string | null
  rating: number | null
  avatar: string | null
  payment_types: string[]
  country: string | null
  registered_at: string | null
  username: string | null
}

export interface SegmentResponse {
  segment: Segment
  user: User
}

export interface SegmentListItem {
  id: number
  name: string
  users: number
}

export interface Executor {
  name: string
  role: string
  location: string
  rating: number
  registrationDate: string
  originalRegistrationDate: string
  daysRegistered: string
  tags: string[]
  stats: {
    reviews: number
    contracts: number
    completedTasks: number
  }
  paymentType: string
  avatar: string
  username: string | null
}

interface TaskAuthor {
  id: number
  username: string | null
  full_name: string
  profile_photo_url: string | null
  prof_level: string | null
  country: string | null
}

export interface Task {
  id: number
  title: string
  description: string
  budget_from: number | null
  budget_to: number | null
  deadline_days: number
  tags: string[]
  status: 'ACCEPTSOFFERS' | 'ATWORK' | string
  created_at: string
  updated_at: string | null
  author: TaskAuthor
  offers_count: number
  pending_offers_count: number
}

export interface AllFreelancers {
  [segment: string]: {
    WANT: SegmentResponse[];
    WILL: SegmentResponse[];
    IN: SegmentResponse[];
  }
} 