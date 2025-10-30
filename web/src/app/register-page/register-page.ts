import { Component, inject, signal } from '@angular/core';
import { AuthService } from '../auth-service/auth-service';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-register-page',
  imports: [
    ReactiveFormsModule,
    CommonModule
  ],
  templateUrl: './register-page.html',
  styleUrl: './register-page.css'
})
export class RegisterPage {
  private authService = inject(AuthService);
  private formBuilder = new FormBuilder();
  protected errorMessage = signal<string | null>(null);
  protected isRegistering = signal(false);

  registerForm = this.formBuilder.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(8)]],
    confirmPassword: ['', [Validators.required]],
  })
  private router = inject(Router);

  protected getFieldError(field: 'email' | 'password' | 'confirmPassword'): string | null {
    const control = this.registerForm.get(field);
    if ((control?.dirty || control?.touched) && control?.errors) {
      if (control.errors['required']) return 'Missing required field';
      if (control.errors['email']) return 'Please enter a valid email address';
      if (control.errors['minlength']) return 'Password must be at least 8 characters';
    }
    return null;
  }

  register() {
    this.errorMessage.set(null);
    if (!this.registerForm.valid) {
      this.registerForm.markAllAsTouched();
      return;
    }

    const { email, password, confirmPassword } = this.registerForm.value;
    if (password !== confirmPassword) {
      this.errorMessage.set('Passwords do not match');
      return;
    }

    this.isRegistering.set(true);
    this.authService.register({ email: email!, password: password! })
      .subscribe({
        next: () => {
          this.isRegistering.set(false);
          this.router.navigate(['/']);
        },
        error: (err: { status: number, error?: { message?: string } }) => {
          this.isRegistering.set(false);
          if (err.status === 409) {
            this.errorMessage.set('An account with this email already exists');
          } else {
            this.errorMessage.set('An error occurred during registration. Please try again.');
          }
        }
      });
  }
}
