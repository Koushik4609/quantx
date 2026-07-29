import React, { useState, useEffect } from 'react';
import { NavBar } from '../components/NavBar';
import { getCourses, getUserProgress, updateUserProgress } from '../api/learning';
import type { Course, Lesson, UserProgress, Quiz } from '../api/learning';
import { BookOpen, CheckCircle, ChevronRight, X, Award, Activity } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export const AcademyPage: React.FC = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [progress, setProgress] = useState<UserProgress[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeCourse, setActiveCourse] = useState<Course | null>(null);
  const [activeLesson, setActiveLesson] = useState<Lesson | null>(null);
  const [quizMode, setQuizMode] = useState(false);
  const [currentQuizIndex, setCurrentQuizIndex] = useState(0);
  const [quizScore, setQuizScore] = useState(0);
  const [quizCompleted, setQuizCompleted] = useState(false);

  const userId = localStorage.getItem('user_id') || '00000000-0000-0000-0000-000000000000';

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [coursesData, progressData] = await Promise.all([
        getCourses(),
        getUserProgress(userId)
      ]);
      setCourses(coursesData);
      setProgress(progressData);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const getCourseProgress = (course: Course) => {
    if (course.lessons.length === 0) return 0;
    const completedLessons = course.lessons.filter(l => 
      progress.some(p => p.lesson_id === l.id && p.completed)
    ).length;
    return Math.round((completedLessons / course.lessons.length) * 100);
  };

  const isLessonCompleted = (lessonId: string) => {
    return progress.some(p => p.lesson_id === lessonId && p.completed);
  };

  const openLesson = (course: Course, lesson: Lesson) => {
    setActiveCourse(course);
    setActiveLesson(lesson);
    setQuizMode(false);
    setCurrentQuizIndex(0);
    setQuizScore(0);
    setQuizCompleted(false);
  };

  const startQuiz = () => {
    setQuizMode(true);
  };

  const handleQuizAnswer = async (optionIndex: number) => {
    if (!activeLesson) return;
    const currentQuiz = activeLesson.quizzes[currentQuizIndex];
    let newScore = quizScore;
    
    if (optionIndex === currentQuiz.correct_option_index) {
      newScore += 1;
      setQuizScore(newScore);
    }

    if (currentQuizIndex + 1 < activeLesson.quizzes.length) {
      setCurrentQuizIndex(currentQuizIndex + 1);
    } else {
      // Quiz finished
      setQuizCompleted(true);
      const finalPercentage = Math.round((newScore / activeLesson.quizzes.length) * 100);
      try {
        await updateUserProgress(userId, activeLesson.id, finalPercentage);
        // Refresh progress
        const p = await getUserProgress(userId);
        setProgress(p);
      } catch (e) {
        console.error("Failed to update progress", e);
      }
    }
  };

  const closeViewer = () => {
    setActiveLesson(null);
    setQuizMode(false);
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <NavBar />
      
      <div className="page-container animate-fade-in" style={{ flex: 1, paddingBottom: '48px' }}>
        <div style={{ marginBottom: '32px' }}>
          <h1 style={{ fontSize: '28px', marginBottom: '8px' }}>Financial Academy</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Master the markets from beginner to advanced.</p>
        </div>

        {loading ? (
           <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', height: '200px' }}>
             <Activity className="animate-spin" size={32} color="var(--accent-blue)" />
           </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
            {['Beginner', 'Intermediate', 'Advanced'].map(level => {
              const levelCourses = courses.filter(c => c.level === level);
              if (levelCourses.length === 0) return null;
              
              return (
                <div key={level}>
                  <h2 style={{ fontSize: '20px', marginBottom: '16px', color: 'var(--accent-blue)' }}>{level}</h2>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '24px' }}>
                    
                    {levelCourses.map(course => {
                      const prog = getCourseProgress(course);
                      return (
                        <div key={course.id} className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                          <h3 style={{ fontSize: '18px', fontWeight: 600 }}>{course.title}</h3>
                          <p style={{ fontSize: '14px', color: 'var(--text-secondary)', flex: 1 }}>{course.description}</p>
                          
                          {/* Progress Bar */}
                          <div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                              <span>Progress</span>
                              <span>{prog}%</span>
                            </div>
                            <div style={{ height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', overflow: 'hidden' }}>
                              <div style={{ width: `${prog}%`, height: '100%', background: 'var(--profit)', transition: 'width 0.5s' }} />
                            </div>
                          </div>
                          
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '8px' }}>
                            {course.lessons.map(lesson => {
                              const isCompleted = isLessonCompleted(lesson.id);
                              return (
                                <button
                                  key={lesson.id}
                                  onClick={() => openLesson(course, lesson)}
                                  className="btn-secondary"
                                  style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.05)', textAlign: 'left' }}
                                >
                                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                    {isCompleted ? <CheckCircle size={16} color="var(--profit)" /> : <BookOpen size={16} color="var(--text-secondary)" />}
                                    <span style={{ fontSize: '14px', fontWeight: 500, color: isCompleted ? 'var(--text-primary)' : 'var(--text-secondary)' }}>
                                      {lesson.order}. {lesson.title}
                                    </span>
                                  </div>
                                  <ChevronRight size={16} />
                                </button>
                              );
                            })}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Lesson / Quiz Modal */}
      {activeLesson && (
        <div style={{ position: 'fixed', inset: 0, zIndex: 100, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '24px', background: 'rgba(0,0,0,0.8)', backdropFilter: 'blur(8px)' }}>
          <div className="glass-panel animate-fade-in" style={{ width: '100%', maxWidth: '800px', height: '80vh', display: 'flex', flexDirection: 'column', position: 'relative', overflow: 'hidden' }}>
            
            {/* Modal Header */}
            <div style={{ padding: '20px 24px', borderBottom: '1px solid rgba(255,255,255,0.1)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(255,255,255,0.02)' }}>
              <div>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>{activeCourse?.title}</div>
                <h2 style={{ fontSize: '20px' }}>{activeLesson.title}</h2>
              </div>
              <button onClick={closeViewer} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}>
                <X size={24} />
              </button>
            </div>
            
            {/* Modal Body */}
            <div style={{ flex: 1, overflowY: 'auto', padding: '24px' }}>
              {!quizMode ? (
                // Lesson Content
                <div className="markdown-body" style={{ color: 'var(--text-primary)', lineHeight: '1.6', fontSize: '16px' }}>
                  <ReactMarkdown>{activeLesson.content}</ReactMarkdown>
                </div>
              ) : quizCompleted ? (
                // Quiz Results
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: '16px', textAlign: 'center' }}>
                  <Award size={64} color="var(--profit)" />
                  <h2 style={{ fontSize: '24px' }}>Quiz Completed!</h2>
                  <p style={{ fontSize: '16px', color: 'var(--text-secondary)' }}>
                    You scored {quizScore} out of {activeLesson.quizzes.length}.
                  </p>
                  <button onClick={closeViewer} className="btn-primary" style={{ marginTop: '16px' }}>Back to Course</button>
                </div>
              ) : (
                // Quiz Questions
                <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', maxWidth: '600px', margin: '0 auto', paddingTop: '40px' }}>
                  <div style={{ fontSize: '14px', color: 'var(--accent-blue)', fontWeight: 600 }}>
                    Question {currentQuizIndex + 1} of {activeLesson.quizzes.length}
                  </div>
                  <h3 style={{ fontSize: '20px', lineHeight: '1.4' }}>
                    {activeLesson.quizzes[currentQuizIndex].question}
                  </h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {activeLesson.quizzes[currentQuizIndex].options.map((opt, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleQuizAnswer(idx)}
                        style={{
                          padding: '16px',
                          background: 'rgba(255,255,255,0.05)',
                          border: '1px solid rgba(255,255,255,0.1)',
                          borderRadius: '8px',
                          color: 'var(--text-primary)',
                          fontSize: '16px',
                          textAlign: 'left',
                          cursor: 'pointer',
                          transition: 'background 0.2s'
                        }}
                        onMouseOver={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.1)'}
                        onMouseOut={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.05)'}
                      >
                        {opt}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            {!quizMode && (
              <div style={{ padding: '20px 24px', borderTop: '1px solid rgba(255,255,255,0.1)', display: 'flex', justifyContent: 'flex-end', background: 'rgba(255,255,255,0.02)' }}>
                {activeLesson.quizzes && activeLesson.quizzes.length > 0 ? (
                  <button onClick={startQuiz} className="btn-primary">Take Quiz</button>
                ) : (
                  <button onClick={() => {
                    updateUserProgress(userId, activeLesson.id, 100).then(() => {
                      fetchData();
                      closeViewer();
                    });
                  }} className="btn-primary">Mark as Completed</button>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
