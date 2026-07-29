import { apiClient, handleApiError } from './client';

export interface Quiz {
  id: string;
  lesson_id: string;
  question: string;
  options: string[];
  correct_option_index: number;
}

export interface Lesson {
  id: string;
  course_id: string;
  title: string;
  content: string;
  order: number;
  quizzes: Quiz[];
}

export interface Course {
  id: string;
  title: string;
  description: string;
  level: string;
  lessons: Lesson[];
}

export interface UserProgress {
  lesson_id: string;
  completed: boolean;
  score: number;
}

export const getCourses = async (): Promise<Course[]> => {
  try {
    const response = await apiClient.get('/learning/courses');
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};

export const getUserProgress = async (userId: string): Promise<UserProgress[]> => {
  try {
    const response = await apiClient.get(`/learning/progress/${userId}`);
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};

export const updateUserProgress = async (userId: string, lessonId: string, score: number): Promise<void> => {
  try {
    await apiClient.post('/learning/progress', {
      user_id: userId,
      lesson_id: lessonId,
      score: score
    });
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};
