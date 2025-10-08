import { Routes } from '@angular/router';
import { LandingPage } from './landing-page/landing-page';

export const routes: Routes = [
    {
        path: '',
        redirectTo: 'landing',
        pathMatch: 'full'
    },
    {
        path: 'landing',
        component: LandingPage
    }
];
