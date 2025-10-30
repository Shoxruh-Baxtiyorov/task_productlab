import React from 'react';

const Footer = () => {
  return (
    <footer className="bg-gradient-to-br from-gray-50 via-slate-50 to-gray-100 border-t border-gray-200 py-16 section-animate">
      <div className="max-w-6xl mx-auto px-6">
        <div className="text-center">
          <div className="flex items-center justify-center space-x-3 mb-6">
            <div className="w-10 h-10 bg-gray-900 rounded-xl flex items-center justify-center">
              <span className="text-white font-medium text-lg">D</span>
            </div>
            <h3 className="text-2xl font-medium text-gray-900">DeadlineTaskBot</h3>
          </div>
          <p className="text-gray-600 mb-8">
            Комплексная платформа-посредник между заказчиками и фрилансерами с полным циклом управления проектами
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
