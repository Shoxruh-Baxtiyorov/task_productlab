import React, { useEffect, useState } from 'react'
import WebApp from '@twa-dev/sdk'
import { checkUserRegistration } from '../services/api'

interface AuthCheckProps {
  children: React.ReactNode
}

const AuthCheck: React.FC<AuthCheckProps> = ({ children }) => {
  const [isLoading, setIsLoading] = useState(true)
  const [isRegistered, setIsRegistered] = useState(false)

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const user = WebApp.initDataUnsafe.user
        
        if (!user) {
          setIsRegistered(false)
          setIsLoading(false)
          return
        }

        const isRegistered = await checkUserRegistration(user.id)
        setIsRegistered(isRegistered)
      } catch (error) {
        console.error('Auth check failed:', error)
        setIsRegistered(false)
      } finally {
        setIsLoading(false)
      }
    }

    checkAuth()
  }, [])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-telegram-button mb-2"></div>
          <p>Проверка доступа...</p>
        </div>
      </div>
    )
  }

  if (!isRegistered) {
    return (
      <div className="flex items-center justify-center min-h-screen p-4">
        <div className="text-center space-y-4">
          <h1 className="text-xl font-bold">Требуется регистрация</h1>
          <p className="text-telegram-hint">
            Для использования приложения необходимо зарегистрироваться в боте.
          </p>
          <button
            onClick={() => WebApp.openTelegramLink(`https://t.me/${import.meta.env.VITE_BOT_USERNAME}?start`)}
            className="w-full py-4 bg-telegram-button text-telegram-buttonText rounded-lg text-sm"
          >
            Перейти к регистрации
          </button>
        </div>
      </div>
    )
  }

  return <>{children}</>
}

export default AuthCheck 