import {Component, inject, OnInit, signal} from '@angular/core';
import {CommonModule} from '@angular/common';
import {ActivatedRoute, Router} from '@angular/router';
import {InstructorsService, RmpReview} from '../services/instructors-service/instructors-service';

@Component({
  selector: 'app-instructor-reviews-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './instructor-reviews-page.html',
  styleUrl: './instructor-reviews-page.css'
})
export class InstructorReviewsPage implements OnInit {
  instructorId = signal<number | null>(null);
  instructorName = signal<string>('');
  reviews = signal<RmpReview[]>([]);
  loading = signal<boolean>(false);
  error = signal<string | null>(null);

  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private instructorsService = inject(InstructorsService);

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      const id = params.get('id');
      if (id) {
        const instructorIdNum = parseInt(id, 10);
        if (!isNaN(instructorIdNum)) {
          this.instructorId.set(instructorIdNum);
          this.loadInstructorName();
          this.loadReviews();
        } else {
          this.error.set('Invalid instructor ID');
        }
      } else {
        this.error.set('No instructor ID provided');
      }
    });
  }

  loadInstructorName(): void {
    if (!this.instructorId()) return;

    this.instructorsService.getInstructors().subscribe({
      next: (instructors) => {
        const instructor = instructors.find(i => i.id === this.instructorId());
        if (instructor) {
          this.instructorName.set(instructor.name);
        }
      },
      error: (err) => {
        console.error('Error loading instructor:', err);
      }
    });
  }

  loadReviews(): void {
    if (!this.instructorId()) return;

    this.loading.set(true);
    this.error.set(null);

    this.instructorsService.getInstructorReviews(this.instructorId()!).subscribe({
      next: (reviews) => {
        this.reviews.set(reviews);
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Error loading reviews:', err);
        this.error.set('Failed to load reviews');
        this.loading.set(false);
      }
    });
  }

  goBack(): void {
    this.router.navigate(['/ratings']);
  }

  formatDate(dateString: string | null): string {
    if (!dateString) return '';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {year: 'numeric', month: 'short', day: 'numeric'});
    } catch {
      return dateString;
    }
  }
}

