import React from 'react';
import { Rocket, Eye, CreditCard, Star, Smartphone } from 'lucide-react';

const HeroSection = () => {
  return (
    <section className="relative py-20 overflow-hidden bg-gradient-to-br from-slate-50 via-gray-50 to-slate-100 section-animate">
      {/* Фоновый баннер */}
      <div className="absolute inset-0">
        {/* Анимированные декоративные элементы */}
        <div className="absolute top-20 left-20 w-32 h-32 rounded-full animate-pulse" style={{
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          boxShadow: '0 0 40px rgba(59, 130, 246, 0.2)',
          animation: 'float 6s ease-in-out infinite'
        }}></div>
        <div className="absolute top-40 right-20 w-24 h-24 rounded-full animate-pulse" style={{
          backgroundColor: 'rgba(139, 92, 246, 0.1)',
          boxShadow: '0 0 40px rgba(139, 92, 246, 0.2)',
          animation: 'float 8s ease-in-out infinite reverse'
        }}></div>
        <div className="absolute bottom-20 left-1/3 w-28 h-28 rounded-full animate-pulse" style={{
          backgroundColor: 'rgba(236, 72, 153, 0.1)',
          boxShadow: '0 0 40px rgba(236, 72, 153, 0.2)',
          animation: 'float 7s ease-in-out infinite'
        }}></div>
        
        {/* Дополнительные анимированные элементы */}
        <div className="absolute top-1/4 right-1/4 w-16 h-16 rounded-full animate-pulse" style={{
          backgroundColor: 'rgba(16, 185, 129, 0.08)',
          boxShadow: '0 0 30px rgba(16, 185, 129, 0.15)',
          animation: 'float 10s ease-in-out infinite'
        }}></div>
        <div className="absolute bottom-1/3 right-1/4 w-20 h-20 rounded-full animate-pulse" style={{
          backgroundColor: 'rgba(245, 158, 11, 0.08)',
          boxShadow: '0 0 35px rgba(245, 158, 11, 0.15)',
          animation: 'float 9s ease-in-out infinite reverse'
        }}></div>
        
        {/* Плавающие точки */}
        <div className="absolute top-32 left-1/3 w-2 h-2 rounded-full animate-ping" style={{
          backgroundColor: 'rgba(59, 130, 246, 0.3)',
          animation: 'float 5s ease-in-out infinite'
        }}></div>
        <div className="absolute top-48 right-1/3 w-1.5 h-1.5 rounded-full animate-ping" style={{
          backgroundColor: 'rgba(139, 92, 246, 0.3)',
          animation: 'float 6s ease-in-out infinite reverse'
        }}></div>
        <div className="absolute bottom-32 left-1/4 w-2.5 h-2.5 rounded-full animate-ping" style={{
          backgroundColor: 'rgba(236, 72, 153, 0.3)',
          animation: 'float 7s ease-in-out infinite'
        }}></div>
      </div>
      
      {/* Основной контент */}
      <div className="relative z-10 max-w-6xl mx-auto px-6">
        <div className="grid lg:grid-cols-2 gap-12 items-center mb-12">
          {/* Левая колонка - основной контент */}
          <div className="text-center lg:text-left">
            {/* Логотип и брендинг */}
            <div className="mb-8">
              <div className="inline-flex items-center gap-2 bg-gray-100 px-4 py-2 rounded-full border border-gray-200">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm font-medium text-gray-700">Платформа для фрилансеров</span>
              </div>
            </div>

            {/* Главный заголовок */}
            <div className="mb-10">
              <h1 className="text-4xl md:text-5xl font-medium text-gray-900 leading-tight mb-6">
                <span className="block">Тысячи</span>
                <span className="block text-gray-900">
                  программистов
                </span>
                <span className="block">готовы работать</span>
              </h1>
              
              <p className="text-lg md:text-xl text-gray-600 leading-relaxed max-w-2xl mx-auto lg:mx-0 mb-8">
                <span className="font-medium text-gray-800">Python</span>, <span className="font-medium text-gray-800">iOS</span>, <span className="font-medium text-gray-800">React</span>, <span className="font-medium text-gray-800">FastAPI</span> разработчики и дизайнеры 
                <br className="hidden md:block" />
                с оплатой <span className="font-medium text-green-600">от 100₽</span> за задачу
              </p>
            </div>

            {/* Кнопки действий */}
            <div className="flex flex-row gap-4 justify-center lg:justify-start mb-12 flex-wrap">
              <button 
                onClick={() => document.getElementById('login').scrollIntoView({ behavior: 'smooth' })}
                className="px-8 py-3 bg-gray-900 hover:bg-gray-800 text-white font-medium text-lg rounded-xl transition-colors flex-shrink-0 whitespace-nowrap"
              >
                <span className="flex items-center gap-3">
                  <Rocket className="w-5 h-5" />
                  Начать работу
                </span>
              </button>
              
              <button 
                onClick={() => document.getElementById('calculator').scrollIntoView({ behavior: 'smooth' })}
                className="px-8 py-3 bg-white text-gray-800 font-medium text-lg rounded-xl border border-gray-200 hover:bg-gray-50 transition-colors flex-shrink-0 whitespace-nowrap"
              >
                <span className="flex items-center gap-3">
                  <Eye className="w-5 h-5" />
                  Посмотреть интерфейс
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </span>
              </button>
            </div>
          </div>

          {/* Правая колонка — фотомозаика компактный */}
          <div className="relative max-w-md mx-auto lg:mx-0">
            <div className="pointer-events-none absolute -inset-4 -z-10 rounded-[2rem] bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 blur-xl"></div>

            {/* Фотографии */}
            <div className="grid grid-cols-2 gap-3">
              {[
                {
                  title: 'Доступные цены',
                  subtitle: 'От 100₽ за задачу',
                  tag: 'Экономия до 40%',
                  src: 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?q=80&w=800&auto=format&fit=crop',
                },
                {
                  title: 'Гарантия качества',
                  subtitle: 'Выполнение в срок',
                  tag: '4.8/5 рейтинг',
                  src: 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?q=80&w=800&auto=format&fit=crop',
                },
                {
                  title: 'Прямая связь',
                  subtitle: 'Общение в Telegram',
                  tag: 'Без посредников',
                  src: 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?q=80&w=800&auto=format&fit=crop',
                },
                {
                  title: 'Все технологии',
                  subtitle: 'Python, React, iOS, FastAPI',
                  tag: '100+ технологий',
                  src: 'https://images.unsplash.com/photo-1461749280684-dccba630e2f6?q=80&w=800&auto=format&fit=crop',
                },
              ].map((card, i) => (
                <figure
                  key={card.title}
                  className={[
                    'group relative overflow-hidden rounded-xl shadow-sm border border-gray-200 bg-white',
                    'aspect-[4/5] sm:aspect-[5/4]',
                    'transition transform hover:-translate-y-1 hover:shadow-md'
                  ].join(' ')}
                >
                  <img
                    src={card.src}
                    alt={card.title}
                    loading="lazy"
                    className="h-full w-full object-cover"
                  />

                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent"></div>

                  <figcaption className="absolute inset-x-0 bottom-0 p-3 text-white">
                    <span className={[
                      'inline-block rounded-md px-2 py-0.5 text-[10px] font-semibold tracking-wide',
                      i === 0 ? 'bg-emerald-500/90' :
                      i === 1 ? 'bg-blue-500/90' :
                      i === 2 ? 'bg-violet-500/90' : 'bg-orange-500/90'
                    ].join(' ')}>
                      {card.tag}
                    </span>

                    <h3 className="mt-1 text-sm font-semibold">{card.title}</h3>
                    <p className="text-xs text-white/90">{card.subtitle}</p>
                  </figcaption>
                </figure>
              ))}
            </div>
          </div>
        </div>

        {/* Дополнительная информация - по центру всего блока */}
        <div className="text-center opacity-0 animate-[fadeIn_0.8s_ease-out_1s_forwards]">
          <div className="inline-flex items-center gap-6 bg-white/80 backdrop-blur-sm rounded-xl px-8 py-4 shadow-lg border border-gray-100/60">
            <div className="flex items-center gap-2">
              <CreditCard className="w-4 h-4 text-green-500" />
              <span className="text-gray-700 text-sm font-medium">Оплата на самозанятость</span>
            </div>
            <div className="w-px h-5 bg-gray-300/60"></div>
            <div className="flex items-center gap-2">
              <Star className="w-4 h-4 text-blue-500" />
              <span className="text-gray-700 text-sm font-medium">Система рейтингов</span>
            </div>
            <div className="w-px h-5 bg-gray-300/60"></div>
            <div className="flex items-center gap-2">
              <Smartphone className="w-4 h-4 text-purple-500" />
              <span className="text-gray-700 text-sm font-medium">Telegram интеграция</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
