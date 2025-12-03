import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { BehaviorSubject, tap, Observable, map } from 'rxjs';
import { jwtDecode, JwtPayload } from 'jwt-decode';

interface CustomTokenPayload extends JwtPayload {
  email?: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private http = inject(HttpClient)

  private loggedIn = new BehaviorSubject<boolean>(this.getLoginStatus());
  isLoggedIn$ = this.loggedIn.asObservable();
  private tokenPayload = new BehaviorSubject<CustomTokenPayload | null>(this.getTokenPayload());
  tokenPayload$ = this.tokenPayload.asObservable();

  login(credentials: { email: string, password: string }) {
    const form = new HttpParams()
      .set('username', credentials.email)
      .set('password', credentials.password);

    const headers = new HttpHeaders({
      'Content-Type': 'application/x-www-form-urlencoded',
    });

    return this.http.post<{
      access_token: string
    }>('/api/identity/token', form.toString(), { headers: headers })
      .pipe(tap({
        next: (res) => {
          if (res && res.access_token) {
            this.setToken(res.access_token);
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

    return this.http.post<{ access_token: string }>('/api/identity/register', form.toString(), { headers: headers })
      .pipe(tap({
        next: (res) => {
          if (res && res.access_token) {
            this.setToken(res.access_token);
          }
        }
      }));
  }

  logout() {
    localStorage.removeItem('access_token');
    this.loggedIn.next(false);
  }

  forgotPassword(email: string): Observable<{ message: string, email: string }> {
    const form = new HttpParams()
      .set('email', email);

    const headers = new HttpHeaders({
      'Content-Type': 'application/x-www-form-urlencoded',
    });

    return this.http.post<{ message: string, email: string }>(
      '/api/identity/forgot-password',
      form.toString(),
      { headers: headers }
    );
  }

  resetPassword(email: string, newPassword: string, resetToken: string): Observable<{ message: string }> {
    const form = new HttpParams()
      .set('email', email)
      .set('new_password', newPassword)
      .set('reset_token', resetToken);

    const headers = new HttpHeaders({
      'Content-Type': 'application/x-www-form-urlencoded',
    });

    return this.http.post<{ message: string }>(
      '/api/identity/reset-password',
      form.toString(),
      { headers: headers }
    );
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  private setToken(token: string) {
    localStorage.setItem('access_token', token);
    this.loggedIn.next(true);
    this.tokenPayload.next(this.getTokenPayload());
  }

  private getTokenPayload(): CustomTokenPayload | null {
    const token = this.getToken();
    if (!token) return null;
    try {
      const payload = jwtDecode<CustomTokenPayload>(token);
      return payload;
    } catch (e) {
      // Invalid token
      return null;
    }
  }

  getLoginStatus() {
    const payload = this.getTokenPayload();
    // payload.exp is in seconds, Date.now() is in milliseconds
    return !!payload && !!payload.exp && Math.floor(Date.now() / 1000) < payload.exp;
  }
}
