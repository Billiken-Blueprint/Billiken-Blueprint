import {Component} from '@angular/core';
import {ButtonDirective, ButtonLabel} from 'primeng/button';
import {CommonModule} from '@angular/common';

@Component({
  selector: 'app-landing-page',
  imports: [
    ButtonDirective,
    CommonModule,
    ButtonLabel
  ],
  templateUrl: './landing-page.html',
  styleUrl: './landing-page.css',
  host: {
    'class': 'block w-full h-full'
  }
})
export class LandingPage {

}
