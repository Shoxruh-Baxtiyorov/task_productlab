import React from 'react';
import Avatar from './ui/Avatar';
import BadgeTop from './ui/BadgeTop';
import Skill from './ui/Skill';

const TOP = [
  {
    initials: "АП",
    name: "Александр Петров",
    rating: 4.9,
    points: 47,
    rate: "1200 ₽/ч",
    skills: ["Python", "FastAPI", "PostgreSQL"],
  },
  {
    initials: "МС",
    name: "Мария Сидорова",
    rating: 4.8,
    points: 42,
    rate: "950 ₽/ч",
    skills: ["React", "TypeScript", "Node.js"],
  },
  {
    initials: "ДК",
    name: "Дмитрий Козлов",
    rating: 4.7,
    points: 38,
    rate: "1500 ₽/ч",
    skills: ["iOS", "Swift", "UIKit"],
  },
  {
    initials: "АВ",
    name: "Анна Волкова",
    rating: 4.9,
    points: 51,
    rate: "800 ₽/ч",
    skills: ["UI/UX Design", "Figma", "Adobe XD"],
  },
  {
    initials: "СИ",
    name: "Сергей Иванов",
    rating: 4.8,
    points: 45,
    rate: "1100 ₽/ч",
    skills: ["DevOps", "Docker", "Kubernetes"],
  },
  {
    initials: "ЕС",
    name: "Елена Смирнова",
    rating: 4.7,
    points: 39,
    rate: "1000 ₽/ч",
    skills: ["Java", "Spring", "Microservices"],
  },
  {
    initials: "АН",
    name: "Артем Новиков",
    rating: 4.6,
    points: 35,
    rate: "750 ₽/ч",
    skills: ["Vue.js", "Laravel", "MySQL"],
  },
  {
    initials: "ОМ",
    name: "Ольга Морозова",
    rating: 4.8,
    points: 41,
    rate: "900 ₽/ч",
    skills: ["Flutter", "Dart", "Firebase"],
  },
];

const NEWBIES = [
  { initials: "АН", name: "Артем Новиков", skills: ["Vue.js", "Laravel"] },
  { initials: "ОМ", name: "Ольга Морозова", skills: ["Flutter", "Dart"] },
  { initials: "ИС", name: "Игорь Соколов", skills: ["Unity", "C#"] },
  { initials: "НК", name: "Наталья Козлова", skills: ["Python", "Data Science"] },
];

const TalentShowcase = ({ selectedSegment, setSelectedSegment }) => {
  const filteredTop = selectedSegment === 'all'
    ? TOP 
    : TOP.filter(p => p.skills.some(skill => skill === selectedSegment));

  return (
    <section id="executors" className="bg-white py-20 transition-all duration-1000 ease-in-out section-animate">
      <div className="max-w-6xl mx-auto px-6">
        {/* Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl font-medium text-gray-900 mb-4">
            Лучшие исполнители и новые лица каждый день
          </h2>
          <p className="text-lg text-gray-600">Находите проверенных специалистов или присоединяйтесь как фрилансер и начните зарабатывать</p>
        </div>

        {/* Grid: Top + Newcomers */}
        <div className="mt-12 grid grid-cols-1 gap-8 lg:grid-cols-3">
          {/* Top performers */}
          <div className="lg:col-span-2">
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-xl font-medium text-gray-900">Топ-исполнители</h3>
              <BadgeTop />
            </div>

            {/* Filter */}
            <div className="mb-6">
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => setSelectedSegment('all')}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    selectedSegment === 'all'
                      ? 'bg-gray-900 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Все
                </button>
                {['Python', 'iOS', 'React', 'FastAPI'].map((segment) => (
                  <button
                    key={segment}
                    onClick={() => setSelectedSegment(segment)}
                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                      selectedSegment === segment
                        ? 'bg-gray-900 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {segment}
                  </button>
                ))}
              </div>
            </div>

            <ul className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              {filteredTop.map((p, i) => (
                <li
                  key={p.name}
                  className="group relative overflow-hidden rounded-xl border border-slate-200/70 bg-white/70 p-4 shadow-sm backdrop-blur transition-all hover:-translate-y-0.5 hover:shadow-lg"
                >
                  <div className="flex items-start gap-3">
                    <Avatar initials={p.initials} i={i} />
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mb-2">
                        <h4 className="truncate text-sm font-semibold text-slate-900">{p.name}</h4>
                        <div className="flex items-center gap-1 text-xs text-amber-500">
                          <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                          </svg>
                          <span className="font-medium text-slate-800">★ {p.rating.toFixed(1)}</span>
                        </div>
                        <span className="text-xs text-slate-500">{p.points} баллов</span>
                      </div>
                      <div className="mb-3 flex flex-wrap gap-1.5">
                        {p.skills.map((s) => (
                          <Skill key={s} label={s} />
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center justify-end">
                    <span className="text-xs font-medium text-slate-900">{p.rate}</span>
                  </div>

                  {/* subtle accent */}
                  <div className="pointer-events-none absolute -right-4 -top-4 h-16 w-16 rounded-full bg-gradient-to-br from-slate-900/5 to-transparent opacity-0 transition-opacity group-hover:opacity-100" />
                </li>
              ))}
            </ul>
          </div>

          {/* Newcomers */}
          <aside className="lg:col-span-1">
            <h3 className="text-xl font-medium text-gray-900 mb-4">Новые исполнители</h3>
            <ul className="space-y-2">
              {NEWBIES.map((n, i) => (
                <li
                  key={n.name}
                  className="flex items-center gap-2 p-2 hover:bg-gray-50 rounded-lg transition-colors"
                >
                  <Avatar initials={n.initials} i={i + 2} />
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-gray-900 truncate">{n.name}</p>
                    <p className="text-xs text-gray-500 truncate">{n.skills.join(', ')}</p>
                  </div>
                </li>
              ))}
            </ul>
          </aside>
        </div>

        {/* CTA Banner */}
        <div className="mt-12 bg-gray-50 rounded-2xl p-8 border border-gray-100">
          <div className="grid items-center gap-6 sm:grid-cols-3">
            <div className="sm:col-span-2">
              <div className="inline-flex items-center gap-2 rounded-full bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700 ring-1 ring-inset ring-emerald-100 mb-3">
                +10 баллов сразу · Бесплатно · Без скрытых комиссий
              </div>
              <h3 className="text-2xl font-medium text-gray-900 mb-3">
                Начать зарабатывать как фрилансер
              </h3>
              <p className="text-gray-600">
                Заполните профиль, пройдите верификацию и получите первые заказы уже сегодня.
              </p>
            </div>
            <div className="sm:justify-self-end">
              <button
                type="button"
                onClick={() => window.open('https://t.me/doindeadlinebot', '_blank')}
                className="w-full rounded-xl bg-emerald-600 px-6 py-3 text-sm font-medium text-white shadow-sm transition-colors hover:bg-emerald-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 sm:w-auto"
              >
                Стать исполнителем
              </button>
            </div>
          </div>
        </div>

        {/* View All Executors Button */}
        <div className="mt-8 text-center">
          <button
            type="button"
            onClick={() => document.getElementById('login').scrollIntoView({ behavior: 'smooth' })}
            className="inline-flex items-center px-6 py-3 bg-gray-900 hover:bg-gray-800 text-white font-medium rounded-xl transition-colors"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Посмотреть всех исполнителей
          </button>
        </div>

        {/* Footer stat */}
        <p className="mt-6 text-center text-sm text-gray-600">
          С нами уже <span className="font-medium text-gray-900">5000+</span> исполнителей
        </p>
      </div>
    </section>
  );
};

export default TalentShowcase;
