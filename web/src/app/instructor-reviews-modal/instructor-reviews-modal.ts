import {Component, inject, Input, Output, EventEmitter, OnInit, OnChanges, signal} from '@angular/core';
import {CommonModule, DatePipe} from '@angular/common';
import {InstructorsService, RmpReview} from '../services/instructors-service/instructors-service';

@Component({
  selector: 'app-instructor-reviews-modal',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './instructor-reviews-modal.html',
  styleUrl: './instructor-reviews-modal.css'
})
export class InstructorReviewsModal implements OnInit, OnChanges {
  @Input() instructorName: string = '';
  @Input() instructorId: number | null = null;
  @Input() isOpen: boolean = false;
  @Output() closeModal = new EventEmitter<void>();

  reviews = signal<RmpReview[]>([]);
  loading = signal<boolean>(false);
  error = signal<string | null>(null);

  private instructorsService = inject(InstructorsService);

  ngOnInit(): void {
    if (this.isOpen && this.instructorId) {
      this.loadReviews();
    }
  }

  ngOnChanges(): void {
    if (this.isOpen && this.instructorId) {
      this.loadReviews();
    }
  }

  loadReviews(): void {
    if (!this.instructorId) return;

    this.loading.set(true);
    this.error.set(null);

    this.instructorsService.getInstructorReviews(this.instructorId).subscribe({
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

  close(): void {
    this.closeModal.emit();
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

