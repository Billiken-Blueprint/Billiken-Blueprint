import {Component, computed, inject, OnInit, signal, ViewEncapsulation} from '@angular/core';
import {CommonModule} from '@angular/common';
import {FormsModule} from '@angular/forms';
import {ActivatedRoute, Router} from '@angular/router';
import {InstructorsService, RmpReview} from '../services/instructors-service/instructors-service';
import {RatingsService} from '../services/ratings-service/ratings-service';
import {CoursesService, Course} from '../services/courses-service/courses-service';

@Component({
  selector: 'app-instructor-reviews-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './instructor-reviews-page.html',
  styleUrl: './instructor-reviews-page.css',
  encapsulation: ViewEncapsulation.None
})
export class InstructorReviewsPage implements OnInit {
  instructorId = signal<number | null>(null);
  instructorName = signal<string>('');
  reviews = signal<RmpReview[]>([]);
  loading = signal<boolean>(false);
  error = signal<string | null>(null);
  editingReview = signal<RmpReview | null>(null);
  editRatingValue = signal<number>(0);
  editDescription = signal<string>('');
  editDifficulty = signal<number | null>(null);
  editWouldTakeAgain = signal<boolean | null>(null);
  editGrade = signal<string>('');
  editAttendance = signal<string>('');
  filterType = signal<'all' | 'rmp' | 'billiken_blueprint'>('all');
  selectedCourse = signal<Course | null>(null);
  courses = signal<Course[]>([]);
  courseSearchText = signal<string>('');
  courseInputFocused = signal<boolean>(false);
  searchFilteredCourses = computed(() => {
    const search = this.courseSearchText().toLowerCase().trim();
    const allCourses = this.courses();
    if (!search) {
      return allCourses;
    }
    return allCourses.filter(course =>
      course.courseCode.toLowerCase().includes(search)
    );
  });
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private instructorsService = inject(InstructorsService);
  private ratingsService = inject(RatingsService);
  private coursesService = inject(CoursesService);

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

    // Load courses for filtering
    this.coursesService.getCourses().subscribe({
      next: (courses) => {
        this.courses.set(courses);
      },
      error: (err) => {
        console.error('Error loading courses:', err);
      }
    });
  }

  onCourseSearchChange(event: any): void {
    const value = event?.target?.value || '';
    this.courseSearchText.set(value);
    if (value && this.selectedCourse()) {
      this.selectedCourse.set(null);
    }
  }

  onCourseFocus(): void {
    this.courseInputFocused.set(true);
  }

  onCourseBlur(): void {
    setTimeout(() => {
      this.courseInputFocused.set(false);
    }, 200);
  }

  selectCourseFromSearch(course: Course): void {
    this.selectedCourse.set(course);
    this.courseSearchText.set('');
    this.courseInputFocused.set(false);
  }

  clearCourseSelection(): void {
    this.selectedCourse.set(null);
    this.courseSearchText.set('');
    this.courseInputFocused.set(false);
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
        // Sort reviews by date (newest first)
        // For RMP reviews, use reviewDate
        // For Billiken Blueprint, use ID as proxy (higher ID = newer)
        const sortedReviews = [...reviews].sort((a, b) => {
          // If both have reviewDate, sort by date (newest first)
          if (a.reviewDate && b.reviewDate) {
            return new Date(b.reviewDate).getTime() - new Date(a.reviewDate).getTime();
          }
          // If only a has reviewDate, a comes first
          if (a.reviewDate && !b.reviewDate) {
            return -1;
          }
          // If only b has reviewDate, b comes first
          if (!a.reviewDate && b.reviewDate) {
            return 1;
          }
          // If neither has reviewDate, sort by ID (higher ID = newer)
          const aId = a.id || 0;
          const bId = b.id || 0;
          return bId - aId;
        });
        this.reviews.set(sortedReviews);
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

  addRating(): void {
    if (this.instructorId()) {
      this.router.navigate(['/ratings/create'], {
        queryParams: {instructorId: this.instructorId()}
      });
    }
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

  editRating(review: RmpReview): void {
    if (!review.id || review.type !== 'billiken_blueprint' || !review.canDelete) {
      return;
    }

    this.editingReview.set(review);
    this.editRatingValue.set(review.quality);
    this.editDescription.set(review.comment);
    this.editDifficulty.set(review.difficulty ?? null);
    this.editWouldTakeAgain.set(review.wouldTakeAgain ?? null);
    this.editGrade.set(review.grade ?? '');
    this.editAttendance.set(review.attendance ?? '');
  }

  cancelEdit(): void {
    this.editingReview.set(null);
    this.editRatingValue.set(0);
    this.editDescription.set('');
    this.editDifficulty.set(null);
    this.editWouldTakeAgain.set(null);
    this.editGrade.set('');
    this.editAttendance.set('');
  }

  saveEdit(): void {
    const review = this.editingReview();
    if (!review || !review.id) return;

    // Validate rating value
    if (this.editRatingValue() < 1 || this.editRatingValue() > 5) {
      this.error.set('Rating must be between 1 and 5');
      return;
    }

    if (!this.editDescription().trim()) {
      this.error.set('Review description cannot be empty');
      return;
    }

    this.error.set(null);

    this.ratingsService.updateRating(review.id, {
      instructorId: review.instructorId?.toString(),
      courseId: undefined, // Keep existing course if any
      rating: this.editRatingValue(),
      description: this.editDescription().trim(),
      difficulty: this.editDifficulty(),
      wouldTakeAgain: this.editWouldTakeAgain(),
      grade: this.editGrade() || null,
      attendance: this.editAttendance() || null,
    }).subscribe({
      next: () => {
        this.cancelEdit();
        this.loadReviews();
      },
      error: (err) => {
        console.error('Error updating rating:', err);
        this.error.set('Failed to update rating. Please try again.');
      }
    });
  }

  deleteRating(review: RmpReview): void {
    if (!review.id || review.type !== 'billiken_blueprint' || !review.canDelete) {
      return;
    }

    if (!confirm('Are you sure you want to delete this rating?')) {
      return;
    }

    this.ratingsService.deleteRating(review.id).subscribe({
      next: () => {
        // Reload reviews after deletion
        this.loadReviews();
      },
      error: (err) => {
        console.error('Error deleting rating:', err);
        this.error.set('Failed to delete rating. Please try again.');
      }
    });
  }

  setFilter(filter: 'all' | 'rmp' | 'billiken_blueprint'): void {
    this.filterType.set(filter);
  }

  filteredReviews(): RmpReview[] {
    const filter = this.filterType();
    let filtered = this.reviews();

    // Filter by type
    if (filter !== 'all') {
      filtered = filtered.filter(review => review.type === filter);
    }

    // Filter by course if selected
    const selectedCourse = this.selectedCourse();
    if (selectedCourse) {
      filtered = filtered.filter(review => {
        // Check courseId first (most reliable)
        if (review.courseId === selectedCourse.id) {
          return true;
        }
        // For RMP reviews, check if course field matches
        if (review.type === 'rmp' && review.course) {
          const normalizedCourseCode = selectedCourse.courseCode.replace(/\s+/g, '').toUpperCase();
          const normalizedReviewCourse = review.course.replace(/\s+/g, '').toUpperCase();
          return normalizedReviewCourse.includes(normalizedCourseCode) ||
            normalizedCourseCode.includes(normalizedReviewCourse);
        }
        // For Billiken Blueprint reviews, check courseCode
        if (review.type === 'billiken_blueprint' && review.courseCode) {
          return review.courseCode === selectedCourse.courseCode;
        }
        return false;
      });
    }

    // Already sorted by loadReviews, but ensure sorting is maintained
    return filtered;
  }

  getReviewDate(review: RmpReview): string | null {
    if (review.reviewDate) {
      return this.formatDate(review.reviewDate);
    }
    return null;
  }
}

