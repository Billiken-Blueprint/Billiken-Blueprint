import {Component} from '@angular/core';
import {CommonModule} from '@angular/common';

@Component({
  selector: 'app-landing-page',
  imports: [
    CommonModule
  ],
  templateUrl: './landing-page.html',
  styleUrl: './landing-page.css',
  host: {
    'class': 'block w-full h-full'
  }
})
export class LandingPage {

}
