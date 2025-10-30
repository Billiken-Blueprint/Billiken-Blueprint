import {Component, inject, OnInit} from '@angular/core';
import {AuthService} from '../auth-service/auth-service';
import {AsyncPipe} from '@angular/common';
import {Card} from 'primeng/card';
import {Menubar} from 'primeng/menubar';
import {MenuItem, MenuItemCommandEvent} from 'primeng/api';
import {Router} from '@angular/router';

@Component({
  selector: 'app-top-banner',
  imports: [
    AsyncPipe,
    Card,
    Menubar
  ],
  templateUrl: './top-banner.html',
  styleUrl: './top-banner.css'
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
  private router = inject(Router);
  tokenPayload = this.authService.tokenPayload$;
  isLoggedIn = this.authService.isLoggedIn$;

  ngOnInit(): void {
    this.tokenPayload.subscribe({
        next: payload => {
          this.items[0].label = payload?.sub ?? "Logged out";
        }
      }
    )
  }

  logout() {
    this.authService.logout();
  }

  navigateToProfile() {
    this.router.navigate(['/profile']);
  }

}
