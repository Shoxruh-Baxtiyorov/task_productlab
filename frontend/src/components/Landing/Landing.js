import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import HeroSection from './components/HeroSection';
import SegmentsSection from './components/SegmentsSection';
import FeaturesSection from './components/FeaturesSection';
import StatisticsSection from './components/StatisticsSection';
import TalentShowcase from './components/TalentShowcase';
import ExamplesSection from './components/ExamplesSection';
import LoginSection from './components/LoginSection';
import Footer from './components/Footer';

const Landing = ({ onTokenSubmit }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [selectedSegment, setSelectedSegment] = useState('all');
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalTasks: 0,
    totalSegments: 0,
    activeContracts: 0
  });

  const mockSegments = [
    'Python', 'JavaScript', 'React', 'Vue.js', 'Node.js', 'PHP', 'Java', 'C#', 
    'Go', 'Rust', 'Swift', 'Kotlin', 'Flutter', 'React Native', 'Docker', 
    'Kubernetes', 'AWS', 'Azure', 'PostgreSQL', 'MongoDB', 'Redis', 'GraphQL',
    'TypeScript', 'Angular', 'Svelte', 'Laravel', 'Django', 'FastAPI', 'Spring',
    'Unity', 'Unreal Engine', 'Figma', 'Adobe XD', 'Sketch', 'Blender', '3D Max'
  ];

  useEffect(() => {
    const updateStats = () => {
      setStats({
        totalUsers: Math.floor(Math.random() * 1000) + 4500, // 4500-5500
        totalTasks: Math.floor(Math.random() * 2000) + 14000, // 14000-16000
        totalSegments: Math.floor(Math.random() * 50) + 400, // 400-450
        activeContracts: Math.floor(Math.random() * 200) + 800 // 800-1000
      });
    };

    updateStats();
    
    const interval = setInterval(updateStats, 300000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-gray-50 to-slate-100">
        <Header 
          mobileMenuOpen={mobileMenuOpen} 
          setMobileMenuOpen={setMobileMenuOpen} 
        />
        
        <HeroSection />
        
        <SegmentsSection segments={mockSegments} />
        
        <FeaturesSection />
        
        <StatisticsSection stats={stats} />
        
        <TalentShowcase 
          selectedSegment={selectedSegment} 
          setSelectedSegment={setSelectedSegment} 
        />
        
        <ExamplesSection 
          activeTab={activeTab} 
          setActiveTab={setActiveTab} 
        />
        
        <LoginSection onTokenSubmit={onTokenSubmit} />
        
        <Footer />
      </div>
    </>
  );
};

export default Landing;
