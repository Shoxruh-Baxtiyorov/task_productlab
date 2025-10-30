import React, { Fragment } from 'react'
import { Menu, Transition } from '@headlessui/react'
import { 
  ChevronDownIcon, 
  ChevronUpIcon,
  ClockIcon
} from '@heroicons/react/24/outline'
import { SortType } from '../utils/sorting'

interface FilterButtonProps {
  children: React.ReactNode;
  onSort: (type: SortType) => void;
}

const FilterButton: React.FC<FilterButtonProps> = ({ children, onSort }) => (
  <Menu as="div" className="relative">
    {({ open }) => (
      <>
        <Menu.Button className={`flex items-center justify-center gap-1.5 w-14 h-9 rounded-lg bg-telegram-secondary transition-all ${
          open 
            ? 'rounded-b-none shadow-none z-[1]' 
            : 'shadow-[0_2px_4px_rgba(0,0,0,0.08)] hover:shadow-[0_3px_6px_rgba(0,0,0,0.12)]'
        }`}>
          {children}
          <ChevronDownIcon className={`w-4 h-4 transition-transform ${
            open ? 'rotate-180' : ''
          }`} />
        </Menu.Button>

        <Transition
          as={Fragment}
          enter="transition ease-out duration-100"
          enterFrom="transform opacity-0 scale-95"
          enterTo="transform opacity-100 scale-100"
          leave="transition ease-in duration-75"
          leaveFrom="transform opacity-100 scale-100"
          leaveTo="transform opacity-0 scale-95"
        >
          <Menu.Items className="absolute right-0 w-48 origin-top rounded-lg bg-telegram-bg border-[0.5px] border-[--tg-theme-text-color]/[0.04] shadow-[0_4px_16px_rgba(0,0,0,0.12)] focus:outline-none -mt-[0.5px] rounded-t-none">
            <div className="py-1">
              <Menu.Item>
                {({ active }) => (
                  <button
                    onClick={() => onSort('asc')}
                    className={`${
                      active ? 'bg-telegram-button/10' : ''
                    } group flex w-full items-center gap-2 px-3 py-2 text-sm`}
                  >
                    <ChevronUpIcon className="w-4 h-4" />
                    По возрастанию
                  </button>
                )}
              </Menu.Item>
              <Menu.Item>
                {({ active }) => (
                  <button
                    onClick={() => onSort('desc')}
                    className={`${
                      active ? 'bg-telegram-button/10' : ''
                    } group flex w-full items-center gap-2 px-3 py-2 text-sm`}
                  >
                    <ChevronDownIcon className="w-4 h-4" />
                    По убыванию
                  </button>
                )}
              </Menu.Item>
              <Menu.Item>
                {({ active }) => (
                  <button
                    onClick={() => onSort('new')}
                    className={`${
                      active ? 'bg-telegram-button/10' : ''
                    } group flex w-full items-center gap-2 px-3 py-2 text-sm`}
                  >
                    <ClockIcon className="w-4 h-4" />
                    Новые
                  </button>
                )}
              </Menu.Item>
            </div>
          </Menu.Items>
        </Transition>
      </>
    )}
  </Menu>
)

export default FilterButton 