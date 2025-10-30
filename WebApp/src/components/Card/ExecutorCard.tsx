import React from 'react'
import { StarIcon } from '@heroicons/react/24/solid'
import { Executor } from '../../types'
import Card from './Card'
import WebApp from '@twa-dev/sdk'
import { getAvatarUrl } from '../../utils/avatar'

interface ExecutorCardProps {
  executor: Executor
}

const ExecutorCard: React.FC<ExecutorCardProps> = ({ executor }) => {
  if (!executor) {
    return null
  }

  const tags = executor.tags || []

  const handleContactClick = () => {
    const url = executor.username 
      ? `https://t.me/${executor.username}`
      : 'https://t.me/doindeadlinebot'
      
    // Используем Telegram WebApp API для открытия ссылки
    WebApp.openTelegramLink(url)
  }

  return (
    <Card>
      <Card.Content>
        <div className="flex gap-3">
          {/* Аватар */}
          <img
            src={getAvatarUrl(executor.name, executor.avatar)}
            alt={executor.name}
            className="w-12 h-12 rounded-full object-cover"
          />
          
          {/* Информация */}
          <div className="flex-1 min-w-0">
            {/* Шапка карточки */}
            <div className="flex justify-between items-start gap-2">
              <div className="min-w-0">
                <h2 className="font-bold text-sm truncate">{executor.name}</h2>
                <div className="flex items-center gap-1.5 text-xs text-telegram-hint mt-0.5">
                  <span className="truncate">{executor.role}</span>
                  <span>•</span>
                  <span className="truncate">{executor.location}</span>
                </div>
              </div>
              <button 
                onClick={handleContactClick}
                className="flex-none px-3 py-1.5 bg-telegram-button text-telegram-buttonText rounded-lg text-xs hover:opacity-90 transition-opacity"
              >
                {executor.username ? 'Написать' : 'Telegram'}
              </button>
            </div>

            {/* Теги */}
            {tags.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mt-2">
                {tags.map((tag, i) => (
                  <span
                    key={i}
                    className="px-2 py-1 text-xs rounded-full bg-[#50B3FF]/10 text-[#50B3FF]"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}

            {/* Статистика */}
            <div className="mt-3 grid grid-cols-3 gap-2 text-xs">
              {/* <div className="bg-telegram-bg rounded-lg p-2">
                <p className="text-telegram-hint">Отзывы</p>
                <p className="font-medium mt-0.5">{executor.stats.reviews}</p>
              </div> */}
              <div className={`${WebApp.colorScheme === 'light' ? 'bg-telegram-bg' : 'bg-telegram-secondary'} rounded-lg p-2`}>
                <p className="text-telegram-hint">Контракты</p>
                <p className="font-medium mt-0.5">{executor.stats.contracts}</p>
              </div>
              <div className={`${WebApp.colorScheme === 'light' ? 'bg-telegram-bg' : 'bg-telegram-secondary'} rounded-lg p-2`}>
                <p className="text-telegram-hint">Сдано</p>
                <p className="font-medium mt-0.5">{executor.stats.completedTasks}</p>
              </div>
            </div>

            {/* Рейтинг и дополнительная информация */}
            <div className="mt-3 flex items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-1">
                  <StarIcon className="w-4 h-4 text-yellow-400" />
                  <span className="font-medium">{executor.rating}</span>
                </div>
                <span className="text-telegram-hint">•</span>
                <span className="text-telegram-hint">{executor.paymentType}</span>
              </div>
              <span className="text-telegram-hint">{executor.registrationDate}</span>
            </div>
          </div>
        </div>
      </Card.Content>
    </Card>
  )
}

export default ExecutorCard 