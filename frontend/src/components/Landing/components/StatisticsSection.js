import React from 'react';

const StatisticsSection = ({ stats }) => {
  return (
    <section id="stats" className="bg-white py-20 border-t border-gray-200 section-animate">
      <div className="max-w-6xl mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-medium text-gray-900 mb-4">
            Платформа в цифрах
          </h2>
          <p className="text-lg text-gray-600 mb-6">
            Статистика успешных фрилансеров на платформе
          </p>
          <div className="inline-flex items-center px-3 py-1 bg-blue-50 text-blue-700 rounded-lg text-sm font-medium">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
            Данные обновляются каждые 5 минут
          </div>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          <div className="text-center">
            <div className="text-5xl font-medium text-gray-900 mb-3 transition-all duration-500">
              {stats.totalUsers.toLocaleString()}+
            </div>
            <div className="text-gray-600">Зарегистрированных исполнителей</div>
          </div>
          <div className="text-center">
            <div className="text-5xl font-medium text-gray-900 mb-3 transition-all duration-500">
              {stats.totalTasks.toLocaleString()}+
            </div>
            <div className="text-gray-600">Выполненных задач</div>
          </div>
          <div className="text-center">
            <div className="text-5xl font-medium text-gray-900 mb-3 transition-all duration-500">
              {stats.totalSegments}+
            </div>
            <div className="text-gray-600">Технологий и навыков</div>
          </div>
          <div className="text-center">
            <div className="text-5xl font-medium text-gray-900 mb-3 transition-all duration-500">
              {stats.activeContracts}
            </div>
            <div className="text-gray-600">Активных контрактов</div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default StatisticsSection;
