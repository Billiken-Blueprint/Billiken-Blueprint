import { Routes } from '@angular/router';
import { LandingPage } from './landing-page/landing-page';
import { LoginPage } from './login-page/login-page';
import { RegisterPage } from './register-page/register-page';
import { QuestionnairePage } from './questionnaire/questionnaire';
import { CoursesPage } from './courses-page/courses-page';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'landing',
    pathMatch: 'full',
  },
  {
    path: 'landing',
    component: LandingPage,
  },
  {
    path: 'login',
    component: LoginPage,
  },
  {
    path: 'register',
    component: RegisterPage,
  },
  {
    path: 'questionnaire',
    component: QuestionnairePage,
  },
  {
    path: 'courses',
    component: CoursesPage,
  }
];
