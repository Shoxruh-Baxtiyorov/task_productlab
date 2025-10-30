import React, { useState } from 'react';

const LoginSection = ({ onTokenSubmit }) => {
  const [token, setToken] = useState('');
  const [tokenError, setTokenError] = useState('');

  const isValidUUID = (uuid) => {
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
    return uuidRegex.test(uuid);
  };

  const handleTokenSubmit = (e) => {
    e.preventDefault();
    setTokenError('');
    
    if (!token.trim()) {
      setTokenError('Пожалуйста, введите токен');
      return;
    }
    
    if (!isValidUUID(token.trim())) {
      setTokenError('Токен должен быть в формате UUID');
      return;
    }
    
    onTokenSubmit(token.trim());
  };

  return (
    <section id="login" className="bg-white py-20 border-t border-gray-100 section-animate">
      <div className="max-w-4xl mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-medium text-gray-900 mb-4">
            Готовы начать работу?
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Получите доступ к платформе и начните находить интересные задачи
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-12 items-center">
          {/* Left side - How to get access */}
          <div className="text-center md:text-left">
            <div className="mb-8">
              <div className="w-16 h-16 bg-gray-900 rounded-xl flex items-center justify-center mb-6 mx-auto md:mx-0">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <h3 className="text-2xl font-medium text-gray-900 mb-4">Как получить доступ?</h3>
              <div className="space-y-4 text-left">
                <div className="flex items-start space-x-3">
                  <div className="w-6 h-6 bg-gray-900 text-white rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0 mt-0.5">1</div>
                  <p className="text-gray-600">Найдите наш Telegram бот <a href="https://t.me/doindeadlinebot" target="_blank" rel="noopener noreferrer" className="font-mono bg-gray-100 px-2 py-1 rounded hover:bg-gray-200 transition-colors">@doindeadlinebot</a></p>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-6 h-6 bg-gray-900 text-white rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0 mt-0.5">2</div>
                  <p className="text-gray-600">Отправьте команду <span className="font-mono bg-gray-100 px-2 py-1 rounded">/token</span></p>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-6 h-6 bg-gray-900 text-white rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0 mt-0.5">3</div>
                  <p className="text-gray-600">Вставьте полученный токен в форму справа</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <h4 className="text-lg font-medium text-gray-900 mb-3">После входа вы получите доступ к:</h4>
              <div className="grid grid-cols-2 gap-3 text-sm text-gray-600">
                <div className="flex items-center space-x-2">
                  <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Поиск задач</span>
                </div>
                <div className="flex items-center space-x-2">
                  <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Отклики на задачи</span>
                </div>
                <div className="flex items-center space-x-2">
                  <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Мессенджер</span>
                </div>
                <div className="flex items-center space-x-2">
                  <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Аналитика</span>
                </div>
              </div>
            </div>
          </div>

          {/* Right side - Login form */}
          <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100">
            <div className="text-center mb-8">
              <h3 className="text-2xl font-medium text-gray-900 mb-2">Вход в систему</h3>
              <p className="text-gray-600">Введите токен для доступа к платформе фрилансера</p>
            </div>
            
            <form onSubmit={handleTokenSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Токен авторизации
                </label>
                <input
                  type="text"
                  value={token}
                  onChange={(e) => {
                    setToken(e.target.value);
                    if (tokenError) setTokenError('');
                  }}
                  placeholder="Вставьте ваш токен (формат UUID)"
                  className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent ${
                    tokenError ? 'border-red-300 focus:ring-red-500' : 'border-gray-300'
                  }`}
                  required
                />
                {tokenError && (
                  <p className="mt-2 text-sm text-red-600">{tokenError}</p>
                )}
              </div>
              
              <button
                type="submit"
                className="w-full bg-gray-900 hover:bg-gray-800 text-white font-medium py-3 px-6 rounded-xl transition-colors"
              >
                Войти в кабинет
              </button>
            </form>

            <div className="mt-6 text-center">
              <a 
                href="https://t.me/doindeadlinebot" 
                target="_blank" 
                rel="noopener noreferrer"
                className="inline-flex items-center text-gray-600 hover:text-gray-900 transition-colors"
              >
                <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.894 8.221l-1.97 9.28c-.145.658-.537.818-1.084.508l-3-2.21-1.446 1.394c-.14.18-.357.295-.6.295-.002 0-.003 0-.005 0l.213-3.054 5.56-5.022c.24-.213-.054-.334-.373-.121l-6.869 4.326-2.96-.924c-.64-.203-.658-.64.135-.954l11.566-4.458c.538-.196 1.006.128.832.941z"/>
                </svg>
                Открыть @doindeadlinebot
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default LoginSection;
