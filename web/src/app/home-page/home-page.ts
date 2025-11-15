import {Component} from '@angular/core';
import {Card} from 'primeng/card';

@Component({
  selector: 'app-home-page',
  imports: [
    Card
  ],
  templateUrl: './home-page.html',
  styleUrl: './home-page.css',
  host: {
    class: 'block w-full h-full flex-grow flex flex-col'
  }
})
export class HomePage {

}
