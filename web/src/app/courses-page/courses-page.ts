import { Component } from '@angular/core';
import { ButtonDirective, ButtonLabel } from 'primeng/button';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-courses-page',
  imports: [ButtonDirective, CommonModule, ButtonLabel],
  templateUrl: './courses-page.html',
  styleUrl: './courses-page.css',
  host: {
    class: 'block w-full h-full',
  },
})
export class CoursesPage {}
