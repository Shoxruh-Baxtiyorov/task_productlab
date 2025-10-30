import React from 'react'
import { StarIcon } from '@heroicons/react/24/solid'
import { Bars3BottomRightIcon } from '@heroicons/react/24/outline'
import SearchInput from './SearchInput'
import FilterButton from './FilterButton'
import { SortType } from '../utils/sorting'
import { Task } from '../types'

interface HeaderProps {
  activeTab: 'executors' | 'tasks'
  setActiveTab: (tab: 'executors' | 'tasks') => void
  onSort: (type: SortType) => void
  onSearch: (query: string, selectedSegments: string[]) => void
  tasks?: Task[]  // Добавляем пропс для задач
}

const Header: React.FC<HeaderProps> = ({ 
  activeTab, 
  setActiveTab,
  onSort,
  onSearch,
  tasks = []
}) => {
  return (
    <header className="header">
      <div className="safe-area-x safe-area-top">
        {/* Tabs Section */}
        <div className="px-4 pt-2">
          <div className="flex justify-center gap-8">
            <button 
              onClick={() => setActiveTab('executors')}
              className={`header-tab ${activeTab === 'executors' ? 'active' : 'inactive'}`}
            >
              Исполнители
              {activeTab === 'executors' && (
                <div className="header-tab-indicator" />
              )}
            </button>
            <button 
              onClick={() => setActiveTab('tasks')}
              className={`header-tab ${activeTab === 'tasks' ? 'active' : 'inactive'}`}
            >
              Задачи
              {activeTab === 'tasks' && (
                <div className="header-tab-indicator" />
              )}
            </button>
          </div>
        </div>

        {/* Search and Filters Section */}
        <div className="mt-3 px-4 pb-3">
          <div className="flex items-start gap-2">
            <SearchInput 
              onSearch={onSearch} 
              activeTab={activeTab}
              tasks={tasks}  // Передаем задачи
            />
            {/* Filter Button */}
            <div className="flex-none">
              {activeTab === 'executors' ? (
                <FilterButton onSort={onSort}>
                  <StarIcon className="w-5 h-5 text-yellow-400" />
                </FilterButton>
              ) : (
                <FilterButton onSort={onSort}>
                  <Bars3BottomRightIcon className="w-5 h-5" />
                </FilterButton>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header 