// 用户相关类型
export interface User {
  id: number
  email: string
  nickname: string | null
  avatar: string | null
  role: 'admin' | 'user'
  created_at: string
}

export interface UserLogin {
  email: string
  password: string
}

export interface UserRegister {
  email: string
  password: string
  nickname?: string
}

export interface Token {
  access_token: string
  token_type: string
}

// 房屋相关类型
export enum HouseStatus {
  DRAFT = '0',
  PUBLISHED = '1',
  UNPUBLISHED = '2'
}

export interface HouseImage {
  id: number
  image_url: string
  is_primary: boolean
  created_at: string
}

export interface House {
  id: number
  title: string
  description: string | null
  price: number
  area: number
  rooms: number
  address: string
  district: string | null
  max_visits_per_day: number
  status: HouseStatus
  user_id: number
  user?: User
  images: HouseImage[]
  created_at: string
  updated_at: string
}

export interface HouseList {
  id: number
  title: string
  price: number
  area: number
  rooms: number
  address: string
  district: string | null
  status: HouseStatus
  user_id: number
  user_nickname: string | null
  primary_image: string | null
  created_at: string
}

export interface HouseCreate {
  title: string
  description?: string
  price: number
  area: number
  rooms: number
  address: string
  district?: string
  max_visits_per_day?: number
}

export interface HouseUpdate {
  title?: string
  description?: string
  price?: number
  area?: number
  rooms?: number
  address?: string
  district?: string
  max_visits_per_day?: number
}

// 分页相关类型
export interface PaginationParams {
  page: number
  page_size: number
}

export interface PaginatedData<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// 预约相关类型
export enum VisitStatus {
  PENDING = '0',
  CONFIRMED = '1',
  CANCELLED = '2'
}

export enum VisitTimeSlot {
  MORNING = 'morning',
  AFTERNOON = 'afternoon'
}

export interface HouseVisit {
  id: number
  house_id: number
  visitor_name: string
  visitor_phone: string
  visit_date: string
  visit_time_slot: VisitTimeSlot
  status: VisitStatus
  remark: string | null
  created_by: number | null
  created_at: string
  updated_at: string
}

export interface AvailableDate {
  date: string
  available: boolean
  remaining: number
}

// 统计相关类型
export interface StatisticsData {
  dates: string[]
  registrations: number[]
  publications: number[]
  page_views: number[]
  unique_visitors: number[]
}

// 操作日志类型
export interface OperationLog {
  _id: string
  user_id: number
  user_email: string
  action: string
  resource_type: string
  resource_id: number
  request_path: string
  request_params: Record<string, any>
  ip_address: string
  user_agent: string
  created_at: string
}

// 响应类型
export interface ResponseData<T = any> {
  code: number
  msg: string
  data: T
}