import React, { useState, useEffect, useRef } from 'react'
import { 
  PaperAirplaneIcon,
  CurrencyDollarIcon,
  XMarkIcon
} from '@heroicons/react/24/outline'
import { Task } from '../../types'
import Card from './Card'
import WebApp from '@twa-dev/sdk'
import { createPortal } from 'react-dom'

interface TaskCardProps {
  task: Task
  botUsername: string
}

const TaskCard: React.FC<TaskCardProps> = ({ task, botUsername }) => {
  const [showModal, setShowModal] = useState(false)
  const [translateY, setTranslateY] = useState(0)
  const [isDragging, setIsDragging] = useState(false)
  const [isAnimatingIn, setIsAnimatingIn] = useState(false)
  const modalRef = useRef<HTMLDivElement>(null)
  const contentRef = useRef<HTMLDivElement>(null)
  let startY = 0

  const DRAG_THRESHOLD = 20
  const CLOSE_THRESHOLD = 150

  // Блокировка прокрутки body при открытом модальном окне
  useEffect(() => {
    if (showModal) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => {
      document.body.style.overflow = ''
    }
  }, [showModal])

  // Обработчики для свайпа
  const handleTouchStart = (e: React.TouchEvent) => {
    const target = e.target as HTMLElement
    if (target.closest('button')) {
      return
    }

    startY = e.touches[0].clientY
    setIsDragging(false)
  }

  const handleTouchMove = (e: React.TouchEvent) => {
    const target = e.target as HTMLElement
    if (target.closest('button')) {
      return
    }

    if (!contentRef.current) return

    const currentY = e.touches[0].clientY
    const deltaY = currentY - startY
    const isScrolledToTop = contentRef.current.scrollTop === 0

    if (isScrolledToTop && deltaY > 0) {
      if (deltaY > DRAG_THRESHOLD || isDragging) {
        setIsDragging(true)
        setTranslateY(deltaY * 0.3)
        e.preventDefault()
      }
    }
  }

  const handleTouchEnd = (e: React.TouchEvent) => {
    const target = e.target as HTMLElement
    if (target.closest('button')) {
      return
    }

    e.preventDefault()
    
    if (translateY > CLOSE_THRESHOLD) {
      setTranslateY(window.innerHeight)
      setTimeout(() => {
        setShowModal(false)
        setTranslateY(0)
      }, 300)
    } else {
      setTranslateY(0)
    }
    setIsDragging(false)
  }

  const handleTaskClick = () => {
    setShowModal(true)
    setTranslateY(window.innerHeight)
    requestAnimationFrame(() => {
      setIsAnimatingIn(true)
      setTranslateY(0)
    })
  }

  const handleClose = () => {
    setTranslateY(window.innerHeight)
    setTimeout(() => {
      setShowModal(false)
      setTranslateY(0)
      setIsAnimatingIn(false)
    }, 300)
  }

  const handleApply = () => {
    handleClose()
    setTimeout(() => {
      WebApp.openTelegramLink(`https://t.me/${botUsername}?start=task${task.id}`)
    }, 100)
  }

  const formatNumber = (num: number): string => {
    if (num % 1000 === 0) {
      if (num >= 1000000) {
        return `${num / 1000000}M`
      }
      return `${num / 1000}K`
    }
    if (num >= 1000) {
      return new Intl.NumberFormat('ru-RU').format(num)
    }
    return num.toString()
  }

  const formatBudget = () => {
    if (task.budget_from && task.budget_to) {
      return `${formatNumber(task.budget_from)} - ${formatNumber(task.budget_to)} ₽`
    }
    if (task.budget_from) {
      return `от ${formatNumber(task.budget_from)} ₽`
    }
    if (task.budget_to) {
      return `до ${formatNumber(task.budget_to)} ₽`
    }
    return 'Договорная'
  }

  return (
    <>
      <Card>
        <Card.Content>
          <div className="space-y-3 cursor-pointer" onClick={handleTaskClick}>
            {/* Заголовок, автор и бюджет */}
            <div className="flex justify-between items-start gap-2">
              <div className="min-w-0">
                <h2 className="font-bold text-sm truncate">{task.title}</h2>
                <div className="flex items-center gap-1.5 text-xs text-telegram-hint mt-0.5">
                  <span className="truncate">{task.author.full_name}</span>
                  {task.author.country && (
                    <>
                      <span>•</span>
                      <span>{task.author.country === 'NOTRUSSIA' ? 'Не РФ' : 'РФ'}</span>
                    </>
                  )}
                  {task.author.prof_level && (
                    <>
                      <span>•</span>
                      <span>{task.author.prof_level}</span>
                    </>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-1 text-sm font-medium">
                <CurrencyDollarIcon className="w-4 h-4" />
                {formatBudget()}
              </div>
            </div>

            {/* Теги */}
            {task.tags && task.tags.length > 0 && (
              <div className="flex flex-wrap gap-1.5">
                {task.tags.map((tag, i) => (
                  <span
                    key={i}
                    className="px-2 py-1 text-xs rounded-full bg-[#50B3FF]/10 text-[#50B3FF]"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}

            {/* Описание */}
            <p className="text-sm text-telegram-text/80 line-clamp-2">
              {task.description}
            </p>

            {/* Статистика и дата */}
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-3">
                {task.offers_count !== undefined && (
                  <span className="text-telegram-hint flex items-center gap-1">
                    <PaperAirplaneIcon className="w-4 h-4 rotate-90" />
                    {task.offers_count}
                  </span>
                )}
              </div>
              <span className="text-telegram-hint">
                {new Date(task.created_at).toLocaleDateString('ru-RU')}
              </span>
            </div>
          </div>
        </Card.Content>
      </Card>

      {/* Выносим модальное окно в портал или на верхний уровень DOM */}
      {createPortal(
        showModal && (
          <div 
            className={`fixed inset-0 z-50 flex items-end justify-center transition-opacity duration-300 modal-container ${
              isAnimatingIn ? 'opacity-100' : 'opacity-0'
            }`}
            style={{ backgroundColor: `rgba(0, 0, 0, ${0.5 - (translateY / 1000)})` }}
            onClick={(e) => {
              if (e.target === e.currentTarget) {
                handleClose()
              }
            }}
            ref={modalRef}
            onTouchStart={handleTouchStart}
            onTouchMove={handleTouchMove}
            onTouchEnd={handleTouchEnd}
          >
            <div 
              className="w-full bg-telegram-bg rounded-t-xl overflow-hidden max-h-[85vh] flex flex-col transform transition-all duration-300 ease-out modal-content"
              style={{ 
                transform: `translateY(${translateY}px)`,
                transition: 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
              }}
              onClick={(e) => e.stopPropagation()}
            >
              {/* Индикатор для перетаскивания */}
              <div className="w-full flex justify-center p-2">
                <div className="w-8 h-1 bg-telegram-hint/20 rounded-full" />
              </div>

              {/* Заголовок */}
              <div className="flex justify-between items-start px-4 py-2">
                <h2 className="text-lg font-bold">{task.title}</h2>
                <button 
                  onClick={handleClose}
                  className="p-1 hover:bg-telegram-text/10 rounded-lg transition-colors"
                >
                  <XMarkIcon className="w-5 h-5" />
                </button>
              </div>

              {/* Контент с прокруткой */}
              <div 
                className="overflow-y-auto flex-1 overscroll-contain"
                ref={contentRef}
              >
                <div className="px-4 pb-12 space-y-4">
                  {/* Информация о заказчике */}
                  <div>
                    <h3 className="font-medium mb-1"><b>Заказчик</b></h3>
                    <div className="flex items-center gap-2 text-sm">
                      <span>{task.author.full_name}</span>
                      {task.author.country && (
                        <span className="text-telegram-hint">
                          • {task.author.country === 'NOTRUSSIA' ? 'Не РФ' : 'РФ'}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Бюджет и сроки */}
                  <div className="flex gap-4">
                    <div>
                      <h3 className="font-medium mb-1"><b>Бюджет</b></h3>
                      <div className="text-sm">{formatBudget()}</div>
                    </div>
                    <div>
                      <h3 className="font-medium mb-1"><b>Срок выполнения</b></h3>
                      <div className="text-sm">{task.deadline_days} дней</div>
                    </div>
                  </div>

                  {/* Описание */}
                  <div>
                    <h3 className="font-medium mb-1"><b>Описание</b></h3>
                    <p className="text-sm whitespace-pre-wrap">{task.description}</p>
                  </div>

                  {/* Теги */}
                  {task.tags && task.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1.5">
                      {task.tags.map((tag, i) => (
                        <span
                          key={i}
                          className="px-2 py-1 text-xs rounded-full bg-[#50B3FF]/10 text-[#50B3FF]"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Кнопка внизу */}
              <div className="px-4 
              pb-8
              py-3.5 
              border-telegram-text/10"
              >
                <button
                  onClick={handleApply}
                  className="w-full py-4 bg-telegram-button text-telegram-buttonText rounded-lg text-sm hover:opacity-90 transition-opacity"
                >
                  Откликнуться
                </button>
              </div>
            </div>
          </div>
        ),
        document.body
      )}
    </>
  )
}

export default TaskCard 