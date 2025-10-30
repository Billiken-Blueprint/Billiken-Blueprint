import {Component, inject, signal} from '@angular/core';
import {AuthService} from '../auth-service/auth-service';
import {FormBuilder, FormControl, FormGroup, FormsModule, ReactiveFormsModule, Validators} from '@angular/forms';
import {Router} from '@angular/router';
import {CommonModule} from '@angular/common';

@Component({
  selector: 'app-login-page',
  imports: [
    ReactiveFormsModule,
    FormsModule,
    CommonModule
  ],
  templateUrl: './login-page.html',
  styleUrl: './login-page.css'
})
export class LoginPage {
  protected errorMessage = signal<string | null>(null);
  private authService = inject(AuthService);
  private formBuilder = inject(FormBuilder);
  credentialsForm = this.formBuilder.group({
    email: new FormControl('', [
      Validators.required,
      Validators.email
    ]),
    password: new FormControl('', [
      Validators.required
    ])
  })
  private router = inject(Router);

  protected getFieldError(field: 'email' | 'password'): string | null {
    const control = this.credentialsForm.get(field);
    if ((control?.dirty || control?.touched) && control?.errors) {
      if (control.errors['required']) return 'Missing required field';
      if (control.errors['email']) return 'Please enter a valid email address';
    }
    return null;
  }

  login() {
    this.errorMessage.set(null);
    if (!this.credentialsForm.valid) {
      this.credentialsForm.markAllAsTouched();
      this.errorMessage.set('Please fill in all required fields');
      return;
    }

    const email = this.credentialsForm.value.email!;
    const password = this.credentialsForm.value.password!;

    this.authService.login({email: email, password: password})
      .subscribe({
        next: result => {
          this.router.navigate(['/'])
        },
        error: (err) => {
          if (err.status === 401) {
            this.errorMessage.set('Incorrect email or password');
          } else {
            this.errorMessage.set('An error occurred during login. Please try again.');
          }
        }
      })
  }
}
