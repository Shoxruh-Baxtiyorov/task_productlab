import React from 'react';

const SegmentsSection = ({ segments }) => {
  return (
    <section className="bg-white py-20 border-t border-gray-100 section-animate">
      <div className="max-w-6xl mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-medium text-gray-900 mb-4">
            Популярные технологии и навыки
          </h2>
          <p className="text-lg text-gray-600">
            На платформе представлены исполнители по всем основным технологиям и направлениям разработки
          </p>
        </div>
        
        <div className="flex flex-wrap justify-center gap-3 mb-8">
          {segments.map((segment, index) => (
            <span 
              key={index}
              className="px-4 py-2 bg-white text-gray-700 rounded-full text-sm font-medium border border-gray-200 hover:bg-gray-50 hover:border-gray-300 transition-colors cursor-pointer"
            >
              {segment}
            </span>
          ))}
        </div>
        
        <div className="text-center">
          <p className="text-gray-600 mb-4">
            И еще <span className="font-medium text-gray-900">100+</span> технологий и направлений
          </p>
          <button 
            onClick={() => document.getElementById('login').scrollIntoView({ behavior: 'smooth' })}
            className="inline-flex items-center px-6 py-3 bg-gray-900 hover:bg-gray-800 text-white font-medium rounded-xl transition-colors"
          >
            <span>Найти исполнителя</span>
            <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </button>
        </div>
      </div>
    </section>
  );
};

export default SegmentsSection;
