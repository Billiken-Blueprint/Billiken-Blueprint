import {Component} from '@angular/core';
import {Card} from 'primeng/card';
import {Textarea} from 'primeng/textarea';

@Component({
  selector: 'app-scheduling-page',
  imports: [Card, Textarea],
  templateUrl: './scheduling-page.html',
  styleUrl: './scheduling-page.css',
  host: {
    class: 'flex-grow flex flex-col'
  }
})
export class SchedulingPage {

}
