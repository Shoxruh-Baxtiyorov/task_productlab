import {useSearchParams} from "react-router-dom";
import {useState, useEffect} from "react";
import {connect} from "react-redux";
import {getMe} from "../actions/users";
import Landing from './Landing/index';
import Dashboard from './Dashboard';

function Welcome ({ getMe, user, loading, error }) {
    const [searchParams] = useSearchParams();
    const [tokenInput, setTokenInput] = useState(() => {
        return sessionStorage.getItem('authToken') || '';
    });

    useEffect(() => {
        const token = searchParams.get('token');
        if (token) {
            sessionStorage.setItem('authToken', token);
            setTokenInput(token);
            if (!user) {
                getMe(token);
            }
        }
    }, [searchParams, user, getMe]);

    const checkToken = (token) => {
        sessionStorage.setItem('authToken', token);
        setTokenInput(token);
        getMe(token);
    }

    if (user === null && !loading) {
        return <Landing onTokenSubmit={checkToken} />;
    }

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center">
                <div className="max-w-md mx-auto p-8 bg-white rounded-2xl shadow-2xl border border-gray-100 animate-fade-in">
                    <div className="text-center">
                        <div className="w-16 h-16 bg-gray-900 rounded-2xl flex items-center justify-center mx-auto mb-6 animate-pulse">
                            <span className="text-white font-medium text-2xl">D</span>
                        </div>
                        
                        <h2 className="text-xl font-medium text-gray-900 mb-2">Загрузка...</h2>
                        <p className="text-gray-500 mb-6">Подождите, мы загружаем ваш профиль</p>
                        
                        <div className="flex justify-center space-x-2">
                            <div className="w-3 h-3 bg-gray-900 rounded-full animate-bounce" style={{animationDelay: '0ms'}}></div>
                            <div className="w-3 h-3 bg-gray-900 rounded-full animate-bounce" style={{animationDelay: '150ms'}}></div>
                            <div className="w-3 h-3 bg-gray-900 rounded-full animate-bounce" style={{animationDelay: '300ms'}}></div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-red-50 to-red-100 flex items-center justify-center">
                <div className="max-w-md mx-auto p-8 bg-white rounded-2xl shadow-2xl border border-red-100 animate-fade-in">
                    <div className="text-center">
                        <div className="w-16 h-16 bg-red-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
                            <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                            </svg>
                        </div>
                        
                        <h2 className="text-xl font-medium text-gray-900 mb-2">Ошибка загрузки</h2>
                        <p className="text-gray-500 mb-6">{error}</p>
                        
                        <button 
                            onClick={() => window.location.reload()}
                            className="bg-gray-900 hover:bg-gray-800 hover:scale-105 active:scale-95 text-white font-medium py-3 px-6 rounded-xl transition-all duration-200 transform"
                        >
                            Попробовать снова
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return <Dashboard user={user} tokenInput={tokenInput} />;
}

const mapStateToProps = state => ({
    user: state.users.user,
    loading: state.users.loading,
    error: state.users.error
});

export default connect(mapStateToProps, {getMe})(Welcome);