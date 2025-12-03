import { Routes } from '@angular/router';
import { inject } from '@angular/core';
import { AuthService } from './services/auth-service/auth-service';

export const routes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    redirectTo: () => {
      const authService = inject(AuthService);
      return authService.getLoginStatus() ? 'home' : 'landing';
    }
  },
  {
    path: 'landing',
    loadComponent: () => import('./landing-page/landing-page').then(m => m.LandingPage),
  },
  {
    path: 'login',
    loadComponent: () => import('./login-page/login-page').then(m => m.LoginPage),
  },
  {
    path: 'register',
    loadComponent: () => import('./register-page/register-page').then(m => m.RegisterPage),
  },
  {
    path: 'questionnaire',
    loadComponent: () => import('./questionnaire/questionnaire').then(m => m.QuestionnairePage),
  },
  {
    path: 'profile',
    loadComponent: () => import('./profile/profile').then(m => m.ProfilePage),
  },
  {
    path: 'courses',
    loadComponent: () => import('./course/course-page').then(m => m.CoursePage),
  },
  {
    path: 'home',
    loadComponent: () => import('./home-page/home-page').then(m => m.HomePage),
  },
  {
    path: 'ratings',
    loadComponent: () => import('./ratings-page/ratings-page').then(m => m.RatingsPage),
  },
  {
    path: 'ratings/create',
    loadComponent: () => import('./ratings-page/create-rating-page/create-rating-page').then(m => m.CreateRatingPage),
  },
  {
    path: 'schedule',
    loadComponent: () => import('./scheduling-page/scheduling-page').then(m => m.SchedulingPage),
  },
  {
    path: 'instructors/:id/reviews',
    loadComponent: () => import('./instructor-reviews-page/instructor-reviews-page').then(m => m.InstructorReviewsPage),
  }
];
