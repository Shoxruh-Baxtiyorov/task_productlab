import React from 'react';

const ExamplesSection = ({ activeTab, setActiveTab }) => {
  const mockTasks = [
    {
      id: 1,
      title: 'Сделать правки для методов nomenclature',
      description: 'Добавить системный вид цены для всех cashboxes, реализовать системное поле для всех товаров, добавить столбец hash для всех товаров и локаций',
      postedBy: 'Table dtb',
      budget: 'по договору',
      deadline: '1д 0ч',
      type: 'Обычная задача',
      tags: ['fastapi', 'python', 'backend'],
      attachments: ['nomenclature.json (47.6 KB)']
    },
    {
      id: 2,
      title: 'Разработка мобильного приложения для доставки',
      description: 'Создать iOS и Android приложение с функционалом заказа, отслеживания доставки и оплаты',
      postedBy: 'Delivery Corp',
      budget: '150,000 ₽',
      deadline: '14д 0ч',
      type: 'Сложная задача',
      tags: ['ios', 'android', 'mobile', 'swift', 'kotlin'],
      attachments: ['design_mockups.zip (2.1 MB)']
    },
    {
      id: 3,
      title: 'Редизайн корпоративного сайта',
      description: 'Современный адаптивный дизайн с улучшенным UX, интеграция с CRM системой',
      postedBy: 'Tech Solutions',
      budget: '80,000 ₽',
      deadline: '7д 0ч',
      type: 'Средняя задача',
      tags: ['ui/ux', 'web', 'react', 'figma'],
      attachments: ['brand_guidelines.pdf (1.8 MB)']
    }
  ];

  const mockOffers = [
    {
      id: 1,
      taskTitle: 'Сделать правки для методов nomenclature',
      taskDescription: 'Добавить системный вид цены для всех cashboxes, реализовать системное поле для всех товаров, добавить столбец hash для всех товаров и локаций',
      clientName: 'Table dtb',
      budget: 'по договору',
      deadline: '1д 0ч',
      status: 'Ожидает ответа',
      submittedAt: '2 часа назад',
      price: '45,000 ₽',
      skills: ['fastapi', 'python', 'backend']
    },
    {
      id: 2,
      taskTitle: 'Разработка мобильного приложения для доставки',
      taskDescription: 'Создать iOS и Android приложение с функционалом заказа, отслеживания доставки и оплаты',
      clientName: 'Delivery Corp',
      budget: '150,000 ₽',
      deadline: '14д 0ч',
      status: 'Рассматривается',
      submittedAt: '1 день назад',
      price: '120,000 ₽',
      skills: ['ios', 'android', 'mobile', 'swift', 'kotlin']
    },
    {
      id: 3,
      taskTitle: 'Редизайн корпоративного сайта',
      taskDescription: 'Современный адаптивный дизайн с улучшенным UX, интеграция с CRM системой',
      clientName: 'Tech Solutions',
      budget: '80,000 ₽',
      deadline: '7д 0ч',
      status: 'Принят',
      submittedAt: '3 дня назад',
      price: '75,000 ₽',
      skills: ['ui/ux', 'web', 'react', 'figma']
    }
  ];

  return (
    <section id="calculator" className="bg-gradient-to-br from-gray-50 via-slate-50 to-gray-100 py-16 border-t border-gray-100 section-animate">
      <div className="max-w-6xl mx-auto px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-medium text-gray-900 mb-4">
            Пример интерфейса фрилансера
          </h2>
          <p className="text-lg text-gray-600">
            Посмотрите, как выглядит личный кабинет для исполнителей
          </p>
        </div>

        {/* Interactive Dashboard Preview */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          {/* Dashboard Header */}
          <div className="bg-white border-b border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gray-900 rounded-lg flex items-center justify-center">
                  <span className="text-white font-semibold text-sm">D</span>
                </div>
                <h3 className="text-lg font-medium text-gray-900">DeadlineTaskBot</h3>
              </div>
              <div className="flex items-center space-x-3">
                <span className="text-sm text-gray-600">Иван Петров</span>
                <div className="w-7 h-7 bg-gray-200 rounded-full flex items-center justify-center">
                  <span className="text-gray-600 text-xs font-medium">ИП</span>
                </div>
              </div>
            </div>
          </div>

          <div className="flex">
            {/* Left Sidebar Menu */}
            <div className="w-56 bg-white border-r border-gray-100">
              <nav className="p-4">
                <div className="space-y-1">
                  <button 
                    onClick={() => setActiveTab('dashboard')}
                    className={`w-full text-left px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                      activeTab === 'dashboard' 
                        ? 'bg-gray-100 text-gray-900' 
                        : 'text-gray-500 hover:bg-gray-50 hover:text-gray-700'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
                      </svg>
                      <span>Обзор</span>
                    </div>
                  </button>

                  <button 
                    onClick={() => setActiveTab('tasks')}
                    className={`w-full text-left px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                      activeTab === 'tasks' 
                        ? 'bg-gray-100 text-gray-900' 
                        : 'text-gray-500 hover:bg-gray-50 hover:text-gray-700'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                      </svg>
                      <span>Задачи</span>
                    </div>
                  </button>

                  <button 
                    onClick={() => setActiveTab('offers')}
                    className={`w-full text-left px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                      activeTab === 'offers' 
                        ? 'bg-gray-100 text-gray-900' 
                        : 'text-gray-500 hover:bg-gray-50 hover:text-gray-700'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a3 3 0 01-3-3v-1" />
                      </svg>
                      <span>Отклики</span>
                    </div>
                  </button>

                  <button 
                    onClick={() => setActiveTab('messenger')}
                    className={`w-full text-left px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                      activeTab === 'messenger' 
                        ? 'bg-gray-100 text-gray-900' 
                        : 'text-gray-500 hover:bg-gray-50 hover:text-gray-700'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                      </svg>
                      <span>Сообщения</span>
                    </div>
                  </button>

                  <button 
                    onClick={() => setActiveTab('analytics')}
                    className={`w-full text-left px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                      activeTab === 'analytics' 
                        ? 'bg-gray-100 text-gray-900' 
                        : 'text-gray-500 hover:bg-gray-50 hover:text-gray-700'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                      <span>Статистика</span>
                    </div>
                  </button>
                </div>
              </nav>
            </div>

            {/* Main Content Area */}
            <div className="flex-1 p-6">
              {/* Dashboard Tab */}
              {activeTab === 'dashboard' && (
                <div>
                  <h2 className="text-xl font-medium text-gray-900 mb-6">Обзор</h2>
                  
                  {/* Stats Cards */}
                  <div className="grid md:grid-cols-3 gap-4 mb-6">
                    <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
                      <div className="flex items-center">
                        <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center mr-3">
                          <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                          </svg>
                        </div>
                        <div>
                          <div className="text-xl font-semibold text-gray-900">12</div>
                          <div className="text-sm text-gray-600">Активных задач</div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
                      <div className="flex items-center">
                        <div className="w-10 h-10 bg-green-50 rounded-lg flex items-center justify-center mr-3">
                          <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        </div>
                        <div>
                          <div className="text-xl font-semibold text-gray-900">45</div>
                          <div className="text-sm text-gray-600">Завершенных</div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
                      <div className="flex items-center">
                        <div className="w-10 h-10 bg-purple-50 rounded-lg flex items-center justify-center mr-3">
                          <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a3 3 0 01-3-3v-1" />
                          </svg>
                        </div>
                        <div>
                          <div className="text-xl font-semibold text-gray-900">8</div>
                          <div className="text-sm text-gray-600">Новых откликов</div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Quick Actions */}
                  <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
                    <h3 className="text-sm font-medium text-gray-900 mb-3">Быстрые действия</h3>
                    <div className="grid md:grid-cols-2 gap-3">
                      <button className="flex items-center p-3 bg-white rounded-lg border border-gray-200 hover:border-gray-300 hover:bg-gray-50 transition-colors">
                        <div className="w-8 h-8 bg-blue-50 rounded-lg flex items-center justify-center mr-3">
                          <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                          </svg>
                        </div>
                        <div className="text-left">
                          <div className="text-sm font-medium text-gray-900">Создать задачу</div>
                          <div className="text-xs text-gray-500">Опубликовать новую задачу</div>
                        </div>
                      </button>
                      
                      <button className="flex items-center p-3 bg-white rounded-lg border border-gray-200 hover:border-gray-300 hover:bg-gray-50 transition-colors">
                        <div className="w-8 h-8 bg-green-50 rounded-lg flex items-center justify-center mr-3">
                          <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                          </svg>
                        </div>
                        <div className="text-left">
                          <div className="text-sm font-medium text-gray-900">Просмотреть отклики</div>
                          <div className="text-xs text-gray-500">Выбрать исполнителя</div>
                        </div>
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Tasks Tab */}
              {activeTab === 'tasks' && (
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-xl font-medium text-gray-900">Мои задачи в работе</h2>
                  </div>
                  
                  <div className="space-y-3">
                    {mockTasks.map((task) => (
                      <div key={task.id} className="bg-white border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors">
                        <div className="flex items-start justify-between mb-3">
                          <h3 className="text-sm font-medium text-gray-900">{task.title}</h3>
                          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                            task.type === 'Сложная задача' ? 'bg-red-50 text-red-700' :
                            task.type === 'Средняя задача' ? 'bg-yellow-50 text-yellow-700' :
                            'bg-green-50 text-green-700'
                          }`}>
                            {task.type}
                          </span>
                        </div>
                        
                        <p className="text-gray-600 text-sm mb-3">{task.description}</p>
                        
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4 text-xs text-gray-500">
                            <span>Бюджет: {task.budget}</span>
                            <span>Дедлайн: {task.deadline}</span>
                          </div>
                          <div className="flex space-x-1">
                            {task.tags.slice(0, 2).map((tag, index) => (
                              <span key={index} className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs">
                                {tag}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Offers Tab */}
              {activeTab === 'offers' && (
                <div>
                  <h2 className="text-xl font-medium text-gray-900 mb-6">Мои отклики на задачи</h2>
                  
                  <div className="space-y-3">
                    {mockOffers.map((offer) => (
                      <div key={offer.id} className="bg-white border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex-1">
                            <h3 className="text-sm font-medium text-gray-900 mb-1">{offer.taskTitle}</h3>
                            <p className="text-xs text-gray-600 mb-2 line-clamp-2">{offer.taskDescription}</p>
                            <div className="flex items-center space-x-4 text-xs text-gray-500">
                              <span>Заказчик: {offer.clientName}</span>
                              <span>Бюджет: {offer.budget}</span>
                              <span>Дедлайн: {offer.deadline}</span>
                            </div>
                          </div>
                          <div className="text-right ml-4">
                            <div className="text-xs text-gray-500 mb-1">Статус</div>
                            <div className={`text-sm font-medium px-2 py-1 rounded text-xs ${
                              offer.status === 'Принят' ? 'bg-green-100 text-green-700' :
                              offer.status === 'Рассматривается' ? 'bg-yellow-100 text-yellow-700' :
                              'bg-gray-100 text-gray-700'
                            }`}>
                              {offer.status}
                            </div>
                            <div className="text-xs text-gray-500 mt-1">{offer.submittedAt}</div>
                          </div>
                        </div>
                        
                        <div className="flex items-center justify-between">
                          <div className="flex space-x-1">
                            {offer.skills.slice(0, 3).map((skill, index) => (
                              <span key={index} className="px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs">
                                {skill}
                              </span>
                            ))}
                          </div>
                          <div className="flex items-center space-x-3">
                            <div className="text-right">
                              <div className="text-xs text-gray-500">Ваша цена</div>
                              <div className="text-sm font-medium text-gray-900">{offer.price}</div>
                            </div>
                            <div className="flex space-x-2">
                              <button className="px-3 py-1.5 bg-gray-600 hover:bg-gray-700 text-white rounded text-xs font-medium transition-colors">
                                Отменить
                              </button>
                              <button className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-medium transition-colors">
                                Изменить
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Messenger Tab */}
              {activeTab === 'messenger' && (
                <div>
                  <h2 className="text-xl font-medium text-gray-900 mb-6">Сообщения</h2>
                  
                  <div className="bg-white border border-gray-200 rounded-lg">
                    <div className="border-b border-gray-200 p-3">
                      <h3 className="text-sm font-medium text-gray-900">Александр Петров</h3>
                      <p className="text-xs text-gray-500">Задача: Разработка мобильного приложения</p>
                    </div>
                    
                    <div className="p-3 space-y-3 h-48 overflow-y-auto">
                      <div className="flex justify-end">
                        <div className="bg-gray-900 text-white px-3 py-2 rounded-lg max-w-xs">
                          <p className="text-sm">Здравствуйте! Когда сможете начать работу?</p>
                          <span className="text-xs text-gray-300 block mt-1">14:30</span>
                        </div>
                      </div>
                      
                      <div className="flex justify-start">
                        <div className="bg-gray-100 text-gray-900 px-3 py-2 rounded-lg max-w-xs">
                          <p className="text-sm">Добрый день! Могу начать завтра. Есть ТЗ?</p>
                          <span className="text-xs text-gray-500 block mt-1">14:32</span>
                        </div>
                      </div>
                      
                      <div className="flex justify-end">
                        <div className="bg-gray-900 text-white px-3 py-2 rounded-lg max-w-xs">
                          <p className="text-sm">Отлично! Отправлю ТЗ в течение часа.</p>
                          <span className="text-xs text-gray-300 block mt-1">14:35</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="border-t border-gray-200 p-3">
                      <div className="flex space-x-2">
                        <input 
                          type="text" 
                          placeholder="Введите сообщение..." 
                          className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-gray-900 focus:border-gray-900 text-sm"
                        />
                        <button className="px-4 py-2 bg-gray-900 hover:bg-gray-800 text-white rounded-lg text-sm font-medium transition-colors">
                          Отправить
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Analytics Tab */}
              {activeTab === 'analytics' && (
                <div>
                  <h2 className="text-xl font-medium text-gray-900 mb-6">Статистика</h2>
                  
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="bg-white border border-gray-200 rounded-lg p-4">
                      <h3 className="text-sm font-medium text-gray-900 mb-3">Задачи</h3>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Активные</span>
                          <span className="font-medium text-blue-600">12</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">В работе</span>
                          <span className="font-medium text-yellow-600">8</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Завершенные</span>
                          <span className="font-medium text-green-600">45</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-white border border-gray-200 rounded-lg p-4">
                      <h3 className="text-sm font-medium text-gray-900 mb-3">Финансы</h3>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Общий бюджет</span>
                          <span className="font-medium text-green-600">2,450,000₽</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Выплачено</span>
                          <span className="font-medium text-blue-600">1,890,000₽</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">В процессе</span>
                          <span className="font-medium text-yellow-600">560,000₽</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="mt-4 bg-white border border-gray-200 rounded-lg p-4">
                    <h3 className="text-sm font-medium text-gray-900 mb-3">Технологии</h3>
                    <div className="grid grid-cols-4 gap-3">
                      {['Python', 'React', 'iOS', 'UI/UX'].map((tech, index) => (
                        <div key={index} className="text-center">
                          <div className="w-12 h-12 bg-gray-50 rounded-lg flex items-center justify-center mx-auto mb-1">
                            <span className="text-gray-700 text-xs font-medium">{tech}</span>
                          </div>
                          <div className="text-xs text-gray-500">{Math.floor(Math.random() * 20) + 10} задач</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ExamplesSection;
