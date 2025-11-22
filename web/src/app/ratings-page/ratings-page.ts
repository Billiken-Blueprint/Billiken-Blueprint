import {Component, inject, OnInit, signal, ViewEncapsulation} from '@angular/core';
import {CommonModule} from '@angular/common';
import {Instructor, InstructorsService} from '../services/instructors-service/instructors-service';
import {Course, CoursesService} from '../services/courses-service/courses-service';
import {Rating, RatingsService} from '../services/ratings-service/ratings-service';

@Component({
  selector: 'app-ratings-page',
  imports: [
    CommonModule
  ],
  templateUrl: './ratings-page.html',
  styleUrl: './ratings-page.css',
  host: {
    class: 'block w-full flex flex-col flex-grow'
  },
  encapsulation: ViewEncapsulation.None
})
export class RatingsPage implements OnInit {
  instructors = signal<Instructor[]>([]);
  selectedInstructor = signal<Instructor | null>(null);
  courses = signal<Course[]>([]);
  selectedCourse = signal<Course | null>(null);
  ratings = signal<Rating[]>([]);
  private instructorsService = inject(InstructorsService);
  private coursesService = inject(CoursesService);
  private ratingsService = inject(RatingsService);

  ngOnInit(): void {
    this.instructorsService.getInstructors().subscribe(instructors => {
      this.instructors.set(instructors);
    });
    this.coursesService.getCourses().subscribe(courses => {
      this.courses.set(courses);
    });
    this.updateRatings();
  }

  selectInstructor(instructor: Instructor) {
    this.selectedInstructor.set(instructor);
    this.updateRatings();
  }

  selectInstructorById(id: string) {
    if (id === '') {
      this.selectedInstructor.set(null);
    } else {
      const instructor = this.instructors().find(i => i.id.toString() === id);
      if (instructor) {
        this.selectInstructor(instructor);
      }
    }
  }

  selectCourse(course: Course) {
    this.selectedCourse.set(course);
    this.updateRatings();
  }

  selectCourseById(id: string) {
    if (id === '') {
      this.selectedCourse.set(null);
    } else {
      const course = this.courses().find(c => c.id.toString() === id);
      if (course) {
        this.selectCourse(course);
      }
    }
  }

  clearFilters() {
    this.selectedInstructor.set(null);
    this.selectedCourse.set(null);
    this.updateRatings();
  }

  updateRatings() {
    const instructorId = this.selectedInstructor()?.id;
    const courseId = this.selectedCourse()?.id;
    this.ratingsService.getRatings(instructorId?.toString(), courseId?.toString()).subscribe({
      next: ratings => {
        this.ratings.set(ratings);
      },
      error: (error) => {
        console.error('Error loading ratings:', error);
        // Set empty array on error to prevent UI issues
        this.ratings.set([]);
      }
    });
  }

  // Calculate combined rating for an instructor (average of RMP and Billiken Blueprint ratings)
  getCombinedRating(instructorId: number | null): {
    average: number;
    bbCount: number;
    rmpRating: number | null
  } | null {
    if (!instructorId) return null;

    const allRatings = this.ratings();
    const bbRatings = allRatings.filter(r => r.instructorId === instructorId && !r.isRmpRating);
    const rmpRating = allRatings.find(r => r.instructorId === instructorId && r.isRmpRating);

    if (bbRatings.length === 0 && !rmpRating) return null;

    const bbAverage = bbRatings.length > 0
      ? bbRatings.reduce((sum, r) => sum + r.rating, 0) / bbRatings.length
      : null;

    if (bbAverage !== null && rmpRating) {
      // Average of both
      return {
        average: (bbAverage + rmpRating.rating) / 2,
        bbCount: bbRatings.length,
        rmpRating: rmpRating.rating
      };
    } else if (bbAverage !== null) {
      // Only Billiken Blueprint
      return {
        average: bbAverage,
        bbCount: bbRatings.length,
        rmpRating: null
      };
    } else if (rmpRating) {
      // Only RMP
      return {
        average: rmpRating.rating,
        bbCount: 0,
        rmpRating: rmpRating.rating
      };
    }

    return null;
  }
}
