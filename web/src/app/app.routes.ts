import {Routes} from '@angular/router';
import {LandingPage} from './landing-page/landing-page';
import {LoginPage} from './login-page/login-page';
import {RegisterPage} from './register-page/register-page';
import {QuestionnairePage} from './questionnaire/questionnaire';
import {ProfilePage} from './profile/profile';
import {CourseInfoPage} from './course-info/course-info';
import {CoursesPage} from './courses-page/courses-page';
import {HomePage} from './home-page/home-page';
import {RatingsPage} from './ratings-page/ratings-page';
import {CreateRatingPage} from './ratings-page/create-rating-page/create-rating-page';


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
    path: 'profile',
    component: ProfilePage
  },
  {
    path: 'course',
    component: CourseInfoPage
  },
  {
    path: 'courses',
    component: CoursesPage,
  },
  {
    path: 'home',
    component: HomePage
  },
  {
    path: 'ratings',
    component: RatingsPage
  },
  {
    path: 'ratings/create',
    component: CreateRatingPage
  }
];
