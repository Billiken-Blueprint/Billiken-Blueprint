import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-degree-roadmap-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './degree-roadmap-page.component.html',
  styleUrls: ['./degree-roadmap-page.component.css'],
})
export class DegreeRoadmapPageComponent {
  recommended: string[] = [];
  loading = false;

  constructor(private http: HttpClient) {}

  fetchSchedule() {
    this.loading = true;

    this.http.get<any>('http://localhost:8000/schedule/1').subscribe({
      next: (data) => {
        this.recommended = data.recommended_courses.map(
          (c: any) => `${c.major} ${c.course_number}`
        );
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      },
    });
  }

  isRecommended(code: string): boolean {
    return this.recommended.includes(code);
  }

  nodeClass(code: string): string {
    return this.isRecommended(code) ? 'node recommended' : 'node';
  }
}
