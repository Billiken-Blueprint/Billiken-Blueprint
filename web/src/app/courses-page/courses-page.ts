import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-courses-page',
  imports: [CommonModule],
  templateUrl: './courses-page.html',
  styleUrl: './courses-page.css',
  host: {
    class: 'block w-full h-full',
  },
})
export class CoursesPage {}
