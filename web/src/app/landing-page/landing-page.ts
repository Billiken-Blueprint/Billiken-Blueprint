import { Component, inject, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth-service/auth-service';

@Component({
  selector: 'app-landing-page',
  imports: [
    CommonModule
  ],
  templateUrl: './landing-page.html',
  styleUrl: './landing-page.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
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
