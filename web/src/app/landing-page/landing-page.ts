import { Component } from '@angular/core';
import {ButtonDirective} from 'primeng/button';

@Component({
  selector: 'app-landing-page',
  imports: [
    ButtonDirective
  ],
  templateUrl: './landing-page.html',
  styleUrl: './landing-page.css',
  host: {
    'class': 'h-full'
  }
})
export class LandingPage {

}
