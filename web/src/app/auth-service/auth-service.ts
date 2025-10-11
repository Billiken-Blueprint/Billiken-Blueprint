import {inject, Injectable} from '@angular/core';
import {HttpClient, HttpHeaders, HttpParams} from '@angular/common/http';
import {tap} from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private http = inject(HttpClient)

  login(credentials: { email: string, password: string }) {
    const form = new HttpParams()
      .set('username', credentials.email)
      .set('password', credentials.password);

    const headers = new HttpHeaders({
      'Content-Type': 'application/x-www-form-urlencoded',
    });

    return this.http.post<{
      access_token: string
    }>('/api/identity/token', form.toString(), {headers: headers})
      .pipe(tap({
        next: (res) => {
          if (res && res.access_token) {
            localStorage.setItem('access_token', res.access_token);
          }
        }
      }));
  }

  register(info: { email: string, password: string }) {
    const form = new HttpParams()
      .set('email', info.email)
      .set('password', info.password);

    const headers = new HttpHeaders({
      'Content-Type': 'application/x-www-form-urlencoded',
    });

    return this.http.post<{ access_token: string }>('/api/identity/register', form.toString(), {headers: headers})
      .pipe(tap({
        next: (res) => {
          if (res && res.access_token) {
            localStorage.setItem('access_token', res.access_token);
          }
        }
      }));
  }
}
