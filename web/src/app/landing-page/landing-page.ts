import {Component, inject} from '@angular/core';
import {CommonModule} from '@angular/common';
import {AuthService} from '../auth-service/auth-service';
import {Router} from '@angular/router';

@Component({
  selector: 'app-landing-page',
  imports: [
    CommonModule
  ],
  templateUrl: './landing-page.html',
  styleUrl: './landing-page.css',
  host: {
    'class': 'block w-full h-full'
  }
})
export class LandingPage {
  private authService = inject(AuthService);
  private router = inject(Router);

  startPlanning() {
    // Check if user is logged in
    const isLoggedIn = this.authService.getToken() !== null;
    
    if (isLoggedIn) {
      // User is logged in, go to home page
      this.router.navigate(['/home']);
    } else {
      // User is not logged in, go to sign up page
      this.router.navigate(['/register']);
    }
  }
}
