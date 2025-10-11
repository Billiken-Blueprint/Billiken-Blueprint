import {Component, inject} from '@angular/core';
import {AuthService} from '../auth-service/auth-service';
import {FormBuilder, FormControl, FormGroup, FormsModule, ReactiveFormsModule, Validators} from '@angular/forms';

@Component({
  selector: 'app-login-page',
  imports: [
    ReactiveFormsModule,
    FormsModule
  ],
  templateUrl: './login-page.html',
  styleUrl: './login-page.css'
})
export class LoginPage {
  private authService = inject(AuthService);
  private formBuilder = inject(FormBuilder);

  errorMessage = '';

  credentialsForm = this.formBuilder.group({
    email: new FormControl('', [
      Validators.required,
      Validators.email
    ]),
    password: new FormControl('', [
      Validators.required
    ])
  })

  login() {
    console.log(this.credentialsForm.value);
    if (!this.credentialsForm.valid) return;

    const email = this.credentialsForm.value.email!;
    const password = this.credentialsForm.value.password!;

    this.authService.login({email: email, password: password})
      .subscribe({
        error: (err) => {
          if (err.status === 401) {
            this.errorMessage = "Incorrect email or password";
          }
        }
      })
  }
}
