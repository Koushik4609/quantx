import { apiClient, handleApiError } from './client';

import { auth } from '../firebase';
import { signInWithEmailAndPassword, createUserWithEmailAndPassword } from 'firebase/auth';

export const login = async (email: string, password: string) => {
  try {
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    const token = await userCredential.user.getIdToken();
    return { idToken: token, user: userCredential.user };
  } catch (error: any) {
    throw new Error(error.message || 'Login failed');
  }
};

export const signup = async (email: string, password: string) => {
  try {
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    const token = await userCredential.user.getIdToken();
    return { idToken: token, user: userCredential.user };
  } catch (error: any) {
    throw new Error(error.message || 'Signup failed');
  }
};

export const getMe = async () => {
  try {
    const response = await apiClient.get('/auth/me');
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};
