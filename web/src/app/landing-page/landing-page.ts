import { Component } from '@angular/core';
import { ButtonDirective } from 'primeng/button';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-landing-page',
  imports: [
    ButtonDirective,
    CommonModule
  ],
  templateUrl: './landing-page.html',
  styleUrl: './landing-page.css',
  host: {
    'class': 'block min-h-screen w-full'
  }
})
export class LandingPage {

}
