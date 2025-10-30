import React from 'react'

interface CardProps {
  children: React.ReactNode;
}

interface CardContentProps {
  children: React.ReactNode;
}

const Card: React.FC<CardProps> & { Content: React.FC<CardContentProps> } = ({ children }) => (
  <div className="overflow-hidden rounded-xl bg-telegram-bg border-[0.5px] border-[--tg-theme-text-color]/[0.04] shadow-[0_2px_8px_rgba(0,0,0,0.06)] transition-shadow hover:shadow-[0_4px_12px_rgba(0,0,0,0.08)]">
    {children}
  </div>
)

Card.Content = ({ children }: CardContentProps) => (
  <div className="p-3">{children}</div>
)

export default Card 