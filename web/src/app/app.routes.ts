import {Routes} from '@angular/router';
import {LandingPage} from './landing-page/landing-page';
import {LoginPage} from './login-page/login-page';
import {RegisterPage} from './register-page/register-page';
import {QuestionnairePage} from './questionnaire/questionnaire';
import {ProfilePage} from './profile/profile';
import {HomePage} from './home-page/home-page';
import {RatingsPage} from './ratings-page/ratings-page';
import {CreateRatingPage} from './ratings-page/create-rating-page/create-rating-page';
import { CoursePage } from './course/course-page';
import {SchedulingPage} from './scheduling-page/scheduling-page';
import { DegreeRoadmapPageComponent } from './degree-roadmap-page/degree-roadmap-page.component';

import {InstructorReviewsPage} from './instructor-reviews-page/instructor-reviews-page';

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
    path: 'courses',
    component: CoursePage
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
  },
  {
    path: 'schedule',
    component: SchedulingPage
  },
  { 
    path: 'degree-roadmap', 
    component: DegreeRoadmapPageComponent },
  {
    path: 'instructors/:id/reviews',
    component: InstructorReviewsPage
  }
];
