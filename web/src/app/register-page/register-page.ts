import {Component, inject} from '@angular/core';
import {AuthService} from '../auth-service/auth-service';
import {FormBuilder, ReactiveFormsModule, Validators} from '@angular/forms';

@Component({
  selector: 'app-register-page',
  imports: [
    ReactiveFormsModule
  ],
  templateUrl: './register-page.html',
  styleUrl: './register-page.css'
})
export class RegisterPage {
  private authSerivce = inject(AuthService);
  private formBuilder = new FormBuilder();


  registerForm = this.formBuilder.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', Validators.required],
    confirmPassword: ['', [Validators.required]],
  })

  register() {
    if (!this.registerForm.valid) return;
    const {email, password, confirmPassword} = this.registerForm.value;
    if (password !== confirmPassword) return;

    this.authSerivce.register({email: email!, password: password!})
      .subscribe({
        error: err => {
          console.log(err);
        }
      })
  }
}
