import React from 'react';
import { Link } from 'react-router-dom';

const Dashboard = ({ user, tokenInput }) => {
    const hasValidToken = tokenInput && tokenInput.trim() !== '';
    const links = [
        {
            route: '/tasks',
            text: 'Мои задачи',
            icon: (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                </svg>
            ),
            description: 'Создавайте и управляйте вашими задачами',
            color: 'blue'
        },
        {
            route: '/offers',
            text: 'Отклики на мои задачи',
            icon: (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a3 3 0 01-3-3v-1M9 12h.01M9 16h.01" />
                </svg>
            ),
            description: 'Просматривайте предложения от исполнителей',
            color: 'green'
        },
        {
            route: '/messenger',
            text: 'Мессенджер',
            icon: (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
            ),
            description: 'Общайтесь с исполнителями напрямую',
            color: 'purple'
        }
    ];

    const stats = [
        {
            label: 'Активных задач',
            value: '0',
            color: 'blue'
        },
        {
            label: 'Завершенных задач',
            value: '0',
            color: 'green'
        },
        {
            label: 'Новых откликов',
            value: '0',
            color: 'purple'
        }
    ];

    return (
        <div className="min-h-screen bg-gray-50">

            <header className="bg-white border-b border-gray-200">
                <div className="max-w-6xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                                <span className="text-white font-bold text-sm">D</span>
                            </div>
                            <h1 className="text-xl font-semibold text-gray-900">DeadlineTaskBot</h1>
                        </div>
                        <div className="flex items-center space-x-3">
                            <span className="text-sm text-gray-600">{user.full_name}</span>
                            <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                                <span className="text-gray-700 font-medium text-sm">
                                    {user.full_name?.charAt(0).toUpperCase()}
                                </span>
                            </div>
                            <button
                                onClick={() => {
                                    sessionStorage.removeItem('authToken');
                                    window.location.reload();
                                }}
                                className="px-3 py-1.5 text-sm text-red-600 hover:text-red-700 hover:bg-red-50 rounded-md transition-colors border border-red-200 hover:border-red-300"
                            >
                                Выйти
                            </button>
                        </div>
                    </div>
                </div>
            </header>


            <div className="max-w-6xl mx-auto px-6 py-8">

                <div className="mb-8">
                    <h2 className="text-2xl font-medium text-gray-900 mb-2">Добро пожаловать</h2>
                    <p className="text-gray-600">Управляйте вашими проектами и задачами</p>
                </div>


                <div className="grid grid-cols-3 gap-6 mb-8">
                    {stats.map((stat, index) => (
                        <div key={index} className="bg-white rounded-lg p-6 border border-gray-200">
                            <div className="text-2xl font-semibold text-gray-900 mb-1">{stat.value}</div>
                            <div className="text-sm text-gray-600">{stat.label}</div>
                        </div>
                    ))}
                </div>


                <div className="bg-white rounded-lg p-6 border border-gray-200 mb-8">
                    <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                            <span className="text-blue-600 font-semibold text-lg">
                                {user.full_name?.charAt(0).toUpperCase()}
                            </span>
                        </div>
                        <div>
                            <h3 className="font-medium text-gray-900">{user.full_name}</h3>
                            <p className="text-sm text-gray-600">ID: {user.id}</p>
                        </div>
                    </div>
                </div>


                <div className="grid md:grid-cols-3 gap-6">
                    {links.map((item, index) => {
                        const isDisabled = item.text === 'Мессенджер';
                        
                        if (isDisabled) {
                            return (
                                <div key={index} className="block">
                                    <div className="bg-gray-100 rounded-lg p-6 border border-gray-200 cursor-not-allowed opacity-60">
                                        <div className="flex items-center mb-4">
                                            <div className="w-10 h-10 bg-gray-200 rounded-lg flex items-center justify-center mr-4">
                                                <div className="text-gray-400">
                                                    {item.icon}
                                                </div>
                                            </div>
                                            <h3 className="font-medium text-gray-500">{item.text}</h3>
                                        </div>
                                        
                                        <p className="text-sm text-gray-500 mb-4">
                                            {item.description}
                                        </p>
                                        
                                        <div className="flex items-center text-gray-400 text-sm font-medium">
                                            <span>Недоступно</span>
                                            <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                            </svg>
                                        </div>
                                    </div>
                                </div>
                            );
                        }
                        
                        return (
                            <Link
                                key={index}
                                to={`${item.route}?token=${tokenInput || ''}`}
                                className="block"
                            >
                                <div className="bg-white rounded-lg p-6 border border-gray-200 hover:border-gray-300 hover:shadow-sm transition-all">
                                    <div className="flex items-center mb-4">
                                        <div className={`w-10 h-10 bg-${item.color}-100 rounded-lg flex items-center justify-center mr-4`}>
                                            <div className={`text-${item.color}-600`}>
                                                {item.icon}
                                            </div>
                                        </div>
                                        <h3 className="font-medium text-gray-900">{item.text}</h3>
                                    </div>
                                    
                                    <p className="text-sm text-gray-600 mb-4">
                                        {item.description}
                                    </p>
                                    
                                    <div className="flex items-center text-blue-600 text-sm font-medium">
                                        <span>Перейти</span>
                                        <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                        </svg>
                                    </div>
                                </div>
                            </Link>
                        );
                    })}
                </div>
            </div>
        </div>
    );
};

export default Dashboard;

