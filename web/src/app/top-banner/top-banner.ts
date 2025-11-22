import {Component, inject, OnInit} from '@angular/core';
import {AuthService} from '../services/auth-service/auth-service';
import {AsyncPipe} from '@angular/common';
import {Menubar} from 'primeng/menubar';
import {MenuItem, MenuItemCommandEvent} from 'primeng/api';
import {Router} from '@angular/router';

@Component({
  selector: 'app-top-banner',
  imports: [
    AsyncPipe,
    Menubar
  ],
  templateUrl: './top-banner.html',
  styleUrl: './top-banner.css',
  standalone: true
})
export class TopBanner implements OnInit {
  items: MenuItem[] = [
    {
      label: 'Email',
      items: [
        {
          label: 'View Profile',
          icon: 'pi pi-user',
          command: () => this.navigateToProfile()
        },
        {
          label: 'Log out',
          icon: 'pi pi-sign-out',
          command: () => this.logout()
        }
      ]
    }
  ]
  private authService = inject(AuthService);
  tokenPayload = this.authService.tokenPayload$;
  isLoggedIn = this.authService.isLoggedIn$;
  private router = inject(Router);

  ngOnInit(): void {
    this.tokenPayload.subscribe({
        next: payload => {
          this.items[0].label = payload?.email ?? "Logged out";
        }
      }
    )
  }

  logout() {
    this.authService.logout();
    this.router.navigate(['/']);
  }

  navigateToProfile() {
    this.router.navigate(['/profile']);
  }

}
