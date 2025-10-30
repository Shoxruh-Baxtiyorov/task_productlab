import { useState, useEffect } from 'react'
import './App.css'
import WebApp from '@twa-dev/sdk'
import Header from './components/Header'
import TaskCard from './components/Card/TaskCard'
import { 
  fetchSegments, 
  fetchSegmentData, 
  convertApiResponseToExecutor, 
  fetchFreelancersBySegment,
  fetchAvailableTasks
} from './services/api'
import { sortExecutors, SortType } from './utils/sorting'
import { ITEMS_PER_PAGE, BOT_USERNAME } from './constants'
import type { Executor, SegmentListItem, Task } from './types'
import ExecutorCard from './components/Card/ExecutorCard'
import AuthCheck from './components/AuthCheck'

function App() {
  const [activeTab, setActiveTab] = useState<'executors' | 'tasks'>('executors')
  const [sortType, setSortType] = useState<SortType>('desc')
  const [searchQuery, setSearchQuery] = useState('')
  const [executors, setExecutors] = useState<Executor[]>([])
  const [loading, setLoading] = useState(true)
  const [visibleItems, setVisibleItems] = useState(ITEMS_PER_PAGE)
  const [filteredExecutors, setFilteredExecutors] = useState<Executor[]>([])
  const [segments, setSegments] = useState<SegmentListItem[]>([])
  const [loadedSegments, setLoadedSegments] = useState<Set<string>>(new Set())
  const [loadedUserIds, setLoadedUserIds] = useState<Set<number>>(new Set())
  const [tasks, setTasks] = useState<Task[]>([])
  const [tasksLoading, setTasksLoading] = useState(false)
  const [visibleTasks, setVisibleTasks] = useState(ITEMS_PER_PAGE)
  const [filteredTasks, setFilteredTasks] = useState<Task[]>([])

  // Загружаем сегменты при монтировании
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setLoading(true)
        const segmentsData = await fetchSegments()
        setSegments(segmentsData)

        const popularSegments = segmentsData
          .sort((a, b) => b.users - a.users)
          .slice(0, 5)

        const allExecutors: Executor[] = []
        const loadedSegmentNames = new Set<string>()
        const userIds = new Set<number>()

        for (const segment of popularSegments) {
          const segmentData = await fetchSegmentData(segment.name)
          if (segmentData) {
            Object.values(segmentData).forEach(typeData => {
              typeData.forEach(response => {
                // Проверяем, не загружен ли уже этот пользователь
                if (!userIds.has(response.user.id)) {
                  userIds.add(response.user.id)
                  allExecutors.push(convertApiResponseToExecutor(response))
                }
              })
            })
            loadedSegmentNames.add(segment.name)
          }
        }

        setExecutors(allExecutors)
        setLoadedSegments(loadedSegmentNames)
        setLoadedUserIds(userIds)
      } catch (error) {
        console.error('Failed to load initial data:', error)
      } finally {
        setLoading(false)
      }
    }

    loadInitialData()
  }, [])

  // Функция для фильтрации исполнителей
  const filterExecutors = (query: string, selectedSegments: string[]) => {
    return executors.filter(executor => {
      const searchLower = query.toLowerCase()
      const matchesSearch = !query || 
        executor.name.toLowerCase().includes(searchLower) ||
        executor.role.toLowerCase().includes(searchLower) ||
        executor.tags.some(tag => tag.toLowerCase().includes(searchLower))

      const matchesSegments = selectedSegments.length === 0 || 
        selectedSegments.every(segment => 
          executor.tags.includes(segment)
        )

      return matchesSearch && matchesSegments
    })
  }

  // Обновляем фильтрацию при изменении executors или поискового запроса
  useEffect(() => {
    setFilteredExecutors(filterExecutors(searchQuery, []))
  }, [executors, searchQuery])

  // Сброс видимых элементов при изменении поиска или сортировки
  useEffect(() => {
    setVisibleItems(ITEMS_PER_PAGE)
  }, [searchQuery, sortType])

  // Функция для загрузки данных сегмента
  const loadSegmentData = async (segment: string) => {
    if (!loadedSegments.has(segment)) {
      try {
        const types: ('WANT' | 'WILL' | 'IN')[] = ['WANT', 'WILL', 'IN']
        const newExecutors: Executor[] = []
        
        // Загружаем данные для всех типов
        for (const type of types) {
          const response = await fetchFreelancersBySegment(segment, type)
          if (response) {
            response.forEach(data => {
              // Проверяем, не загружен ли уже этот пользователь
              if (!loadedUserIds.has(data.user.id)) {
                loadedUserIds.add(data.user.id)
                newExecutors.push(convertApiResponseToExecutor(data))
              }
            })
          }
        }

        if (newExecutors.length > 0) {
          setExecutors(prev => [...prev, ...newExecutors])
          setLoadedUserIds(new Set(loadedUserIds))
        }
        setLoadedSegments(prev => new Set(prev).add(segment))
      } catch (error) {
        console.error(`Failed to load data for segment ${segment}:`, error)
      }
    }
  }

  // Обновляем функцию handleSearch
  const handleSearch = async (query: string, selectedSegments: string[]) => {
    setSearchQuery(query)
    setLoading(true)
    
    try {
      // Загружаем данные для выбранных сегментов
      for (const segment of selectedSegments) {
        await loadSegmentData(segment)
      }

      // Если есть текст поиска, проверяем совпадения в незагруженных сегментах
      if (query) {
        const matchingSegments = segments
          .filter(segment => 
            !loadedSegments.has(segment.name) &&
            segment.name.toLowerCase().includes(query.toLowerCase())
          )
          .slice(0, 3)

        for (const segment of matchingSegments) {
          await loadSegmentData(segment.name)
        }
      }

      // Применяем фильтрацию
      setFilteredExecutors(filterExecutors(query, selectedSegments))
    } catch (error) {
      console.error('Error during search:', error)
    } finally {
      setLoading(false)
    }
  }

  // Сортируем отфильтрованных исполнителей
  const sortedExecutors = sortExecutors(filteredExecutors, sortType)

  // Получаем видимых исполнителей
  const visibleExecutors = sortedExecutors.slice(0, visibleItems)

  // Обработчик "Загрузить ещё"
  const handleLoadMore = () => {
    setVisibleItems(prev => prev + ITEMS_PER_PAGE)
  }

  // Обработчик сортировки
  const handleSort = (type: SortType) => {
    setSortType(type)
  }

  // Функция для фильтрации задач
  const filterTasks = (query: string, selectedSegments: string[]) => {
    return tasks.filter(task => {
      // Проверяем совпадение по поисковому запросу
      const searchLower = query.toLowerCase()
      const matchesSearch = !query || 
        task.title.toLowerCase().includes(searchLower) ||
        task.description.toLowerCase().includes(searchLower) ||
        task.tags.some(tag => tag.toLowerCase().includes(searchLower))

      // Проверяем совпадение по выбранным сегментам
      const matchesSegments = selectedSegments.length === 0 || 
        selectedSegments.some(segment => 
          task.tags.some(tag => tag.toLowerCase() === segment.toLowerCase())
        )

      // Задача должна соответствовать и поиску, и выбранным сегментам
      return matchesSearch && matchesSegments
    })
  }

  // Обработчик поиска для задач
  const handleTaskSearch = (query: string, selectedSegments: string[]) => {
    const filtered = filterTasks(query, selectedSegments)
    setFilteredTasks(filtered)
  }

  // Обработчик сортировки задач
  const handleTaskSort = (type: SortType) => {
    const sorted = [...filteredTasks].sort((a, b) => {
      switch (type) {
        case 'new':
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        case 'asc':
          return (a.budget_from || 0) - (b.budget_from || 0)
        case 'desc':
          return (b.budget_from || 0) - (a.budget_from || 0)
        default:
          return 0
      }
    })
    setFilteredTasks(sorted)
  }

  // Обновляем эффект загрузки задач
  useEffect(() => {
    if (activeTab === 'tasks') {
      const loadTasks = async () => {
        setTasksLoading(true)
        try {
          const availableTasks = await fetchAvailableTasks()
          setTasks(availableTasks)
          setFilteredTasks(availableTasks) // Инициализируем отфильтрованные задачи
        } catch (error) {
          console.error('Failed to load tasks:', error)
        } finally {
          setTasksLoading(false)
        }
      }

      loadTasks()
    }
  }, [activeTab])

  // Добавляем обработчик для загрузки дополнительных задач
  const handleLoadMoreTasks = () => {
    setVisibleTasks(prev => prev + ITEMS_PER_PAGE)
  }

  // В функции App добавляем эффект для сброса состояний при переключении вкладок
  useEffect(() => {
    setVisibleTasks(ITEMS_PER_PAGE)
    if (activeTab === 'tasks') {
      setFilteredTasks(tasks) // Сбрасываем фильтрацию при переключении на вкладку задач
    }
  }, [activeTab, tasks])

  // Инициализируем Telegram Web App
  WebApp.ready()
  WebApp.expand()

  return (
    <AuthCheck>
      <div className="min-h-screen bg-telegram-bg overflow-x-hidden">
        <Header 
          activeTab={activeTab} 
          setActiveTab={setActiveTab} 
          onSort={activeTab === 'executors' ? handleSort : handleTaskSort} 
          onSearch={activeTab === 'executors' ? handleSearch : handleTaskSearch}
          tasks={tasks}  // Передаем задачи
        />

        {/* Main Content */}
        <main className="safe-area-x safe-area-bottom">
          <div className="px-4 py-3 space-y-3">
            {loading ? (
              <div className="text-center py-4">Loading...</div>
            ) : activeTab === 'executors' ? (
              <>
                {visibleExecutors.length > 0 ? (
                  <>
                    {visibleExecutors.map((executor, index) => (
                      <ExecutorCard key={`${executor.name}-${index}`} executor={executor} />
                    ))}
                    
                    {/* Load More Button */}
                    {visibleItems < sortedExecutors.length && (
                      <button
                        onClick={handleLoadMore}
                        className="w-full py-2 px-4 bg-telegram-button text-telegram-buttonText rounded-lg text-sm hover:opacity-90 transition-opacity"
                      >
                        Загрузить ещё ({sortedExecutors.length - visibleItems})
                      </button>
                    )}
                  </>
                ) : (
                  <div className="text-center py-4 text-telegram-hint">
                    Ничего не найдено
                  </div>
                )}
              </>
            ) : (
              <>
                {tasksLoading ? (
                  <div className="text-center py-4">Loading...</div>
                ) : filteredTasks.length > 0 ? (
                  <>
                    {filteredTasks.slice(0, visibleTasks).map((task) => (
                      <TaskCard 
                        key={task.id} 
                        task={task} 
                        botUsername={BOT_USERNAME}
                      />
                    ))}
                    
                    {visibleTasks < filteredTasks.length && (
                      <button
                        onClick={handleLoadMoreTasks}
                        className="w-full py-2 px-4 bg-telegram-button text-telegram-buttonText rounded-lg text-sm hover:opacity-90 transition-opacity"
                      >
                        Загрузить ещё ({filteredTasks.length - visibleTasks})
                      </button>
                    )}
                  </>
                ) : (
                  <div className="text-center py-4 text-telegram-hint">
                    Нет доступных задач
                  </div>
                )}
              </>
            )}
          </div>
        </main>
      </div>
    </AuthCheck>
  )
}

export default App