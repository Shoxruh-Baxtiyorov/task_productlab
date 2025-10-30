import React, { useState, useEffect, useRef } from 'react'
import { 
  MagnifyingGlassIcon, 
  XMarkIcon 
} from '@heroicons/react/24/outline'
import { fetchSegments } from '../services/api'
import type { SegmentListItem, Task } from '../types'

interface SearchInputProps {
  onSearch: (query: string, selectedSegments: string[]) => void
  activeTab: 'executors' | 'tasks'
  tasks?: Task[]
}

interface Suggestion {
  text: string
  type: 'segment'
  users?: number
}

const SearchInput: React.FC<SearchInputProps> = ({ onSearch, activeTab, tasks = [] }) => {
  const [query, setQuery] = useState('')
  const [segments, setSegments] = useState<SegmentListItem[]>([])
  const [suggestions, setSuggestions] = useState<Suggestion[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [selectedSegments, setSelectedSegments] = useState<string[]>([])
  const inputRef = useRef<HTMLInputElement>(null)
  const suggestionsRef = useRef<HTMLDivElement>(null)

  // Загружаем сегменты при монтировании
  useEffect(() => {
    const loadSegments = async () => {
      if (activeTab === 'executors') {
        const data = await fetchSegments()
        setSegments(data.sort((a, b) => b.users - a.users))
      } else {
        // Для вкладки задач собираем уникальные теги из всех задач
        const uniqueTags = new Set<string>()
        tasks.forEach(task => {
          task.tags.forEach(tag => uniqueTags.add(tag))
        })
        
        // Преобразуем в формат SegmentListItem
        const taskSegments: SegmentListItem[] = Array.from(uniqueTags).map((tag, index) => ({
          id: index,
          name: tag,
          users: tasks.filter(task => task.tags.includes(tag)).length
        }))
        
        setSegments(taskSegments.sort((a, b) => b.users - a.users))
      }
    }
    loadSegments()
  }, [activeTab, tasks])

  // Закрываем подсказки при клике вне компонента
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        suggestionsRef.current && 
        !suggestionsRef.current.contains(event.target as Node) &&
        !inputRef.current?.contains(event.target as Node)
      ) {
        setShowSuggestions(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const showTopSegments = () => {
    // Показываем топ-5 сегментов, исключая уже выбранные
    setSuggestions(
      segments
        .filter(segment => !selectedSegments.includes(segment.name))
        .sort((a, b) => b.users - a.users)
        .slice(0, 5)
        .map(segment => ({
          text: segment.name,
          type: 'segment',
          users: segment.users
        }))
    )
    setShowSuggestions(true)
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setQuery(value)

    // Если поле пустое, показываем топ сегментов
    if (!value.trim()) {
      showTopSegments()
      return
    }

    // Фильтруем сегменты по введенному тексту
    const searchLower = value.toLowerCase()
    const filteredSuggestions = segments
      .filter(segment => 
        !selectedSegments.includes(segment.name) && 
        segment.name.toLowerCase().includes(searchLower)
      )
      .slice(0, 5)
      .map(segment => ({
        text: segment.name,
        type: 'segment' as const,
        users: segment.users
      }))

    setSuggestions(filteredSuggestions)
    setShowSuggestions(true)
  }

  const handleSuggestionClick = (suggestion: Suggestion) => {
    const newSelectedSegments = [...selectedSegments, suggestion.text]
    setSelectedSegments(newSelectedSegments)
    setShowSuggestions(false)
    setQuery('')
    onSearch('', newSelectedSegments)
  }

  const handleRemoveSegment = (segment: string) => {
    const newSelectedSegments = selectedSegments.filter(s => s !== segment)
    setSelectedSegments(newSelectedSegments)
    onSearch(query, newSelectedSegments)
  }

  const handleClear = () => {
    setQuery('')
    setSelectedSegments([])
    onSearch('', [])
    if (inputRef.current) {
      inputRef.current.focus()
    }
  }

  return (
    <div className="relative flex-1">
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={handleInputChange}
          onFocus={() => {
            if (!query) {
              showTopSegments()
            }
            setShowSuggestions(true)
          }}
          className="w-full bg-telegram-secondary rounded-lg pl-10 pr-10 py-2 text-sm 
            text-[var(--tg-theme-text-color)] 
            bg-[var(--tg-theme-secondary-bg-color)] 
            placeholder:text-[var(--tg-theme-hint-color)]
            focus:outline-none focus:ring-2 
            focus:ring-[var(--tg-theme-button-color)]
            shadow-[0_2px_4px_rgba(0,0,0,0.08)] 
            hover:shadow-[0_3px_6px_rgba(0,0,0,0.12)] 
            transition-shadow"
          placeholder="Поиск..."
        />
        <MagnifyingGlassIcon className="absolute left-3 top-2.5 h-4 w-4 text-[var(--tg-theme-hint-color)]" />
        {(query || selectedSegments.length > 0) && (
          <button
            onClick={handleClear}
            className="absolute right-3 top-2.5"
          >
            <XMarkIcon className="h-4 w-4 text-[var(--tg-theme-hint-color)]" />
          </button>
        )}
      </div>

      {/* Выбранные сегменты */}
      {selectedSegments.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-2">
          {selectedSegments.map((segment) => (
            <span
              key={segment}
              className="px-2 py-1 text-xs 
                bg-[var(--tg-theme-button-color)]/10 
                text-[var(--tg-theme-button-color)] 
                rounded-full flex items-center gap-1"
            >
              {segment}
              <XMarkIcon
                className="w-3 h-3 cursor-pointer"
                onClick={() => handleRemoveSegment(segment)}
              />
            </span>
          ))}
        </div>
      )}

      {/* Подсказки */}
      {showSuggestions && suggestions.length > 0 && (
        <div 
          ref={suggestionsRef}
          className="absolute z-10 mt-1 w-full 
            bg-[var(--tg-theme-bg-color)]
            border-[var(--tg-theme-text-color)]/[0.04]
            shadow-[0_4px_16px_rgba(0,0,0,0.12)] 
            rounded-lg py-1"
        >
          {suggestions.map((suggestion, index) => (
            <button
              key={index}
              onClick={() => handleSuggestionClick(suggestion)}
              className="w-full px-4 py-2 text-left text-sm 
                text-[var(--tg-theme-text-color)]
                hover:bg-[var(--tg-theme-hint-color)]/10 
                flex justify-between items-center"
            >
              <span>{suggestion.text}</span>
              {suggestion.users && (
                <span className="text-[var(--tg-theme-hint-color)] text-xs">
                  {suggestion.users} users
                </span>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

export default SearchInput 