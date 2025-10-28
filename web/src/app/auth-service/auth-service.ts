import {inject, Injectable} from '@angular/core';
import {HttpClient, HttpHeaders, HttpParams} from '@angular/common/http';
import {BehaviorSubject, tap} from 'rxjs';
import {jwtDecode, JwtPayload} from 'jwt-decode';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private http = inject(HttpClient)

  private loggedIn = new BehaviorSubject<boolean>(this.getLoginStatus());
  isLoggedIn$ = this.loggedIn.asObservable();
  private tokenPayload = new BehaviorSubject<JwtPayload | null>(this.getTokenPayload());
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
    }>('/api/identity/token', form.toString(), {headers: headers})
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

    return this.http.post<{ access_token: string }>('/api/identity/register', form.toString(), {headers: headers})
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

  private getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  private setToken(token: string) {
    localStorage.setItem('access_token', token);
    this.loggedIn.next(true);
    this.tokenPayload.next(this.getTokenPayload());
  }

  private getTokenPayload(): JwtPayload | null {
    const token = this.getToken();
    if (!token) return null;
    const payload = jwtDecode(token);
    console.log(Date.now())
    console.log(payload.exp);
    return payload;
  }

  private getLoginStatus() {
    const payload = this.getTokenPayload();
    return !!payload && !!payload.exp && Date.now() / 1000 < payload.exp;
  }
}
