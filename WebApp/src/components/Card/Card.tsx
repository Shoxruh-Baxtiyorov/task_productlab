import WebApp from '@twa-dev/sdk';
import React from 'react'

interface CardProps {
  children: React.ReactNode;
}

interface CardContentProps {
  children: React.ReactNode;
}

const Card: React.FC<CardProps> & { Content: React.FC<CardContentProps> } = ({ children }) => (
  <div className={`
    overflow-hidden rounded-xl 
    ${WebApp.colorScheme === 'light' ? 'bg-telegram-bg' : 'bg-telegram-secondary'}
    border-[1px_solid_var(--tg-theme-secondary-bg-color)]
    shadow-[0_2px_8px_rgba(0,0,0,0.06)] 
    transition-shadow
    hover:shadow-[0_4px_12px_rgba(0,0,0,0.08)]
  `}>
    {children}
  </div>
)

Card.Content = ({ children }: CardContentProps) => (
  <div className="p-3">{children}</div>
)

export default Card 