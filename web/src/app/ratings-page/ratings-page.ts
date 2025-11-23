import {Component, inject, OnInit, signal, ViewEncapsulation} from '@angular/core';
import {CommonModule} from '@angular/common';
import {Instructor, InstructorsService} from '../services/instructors-service/instructors-service';
import {Course, CoursesService} from '../services/courses-service/courses-service';
import {Rating, RatingsService} from '../services/ratings-service/ratings-service';
import {Router} from '@angular/router';

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
  selectedDepartment = signal<string>('all'); // 'all', 'CSCI', 'MATH'
  ratings = signal<Rating[]>([]);
  
  // Get filtered instructors based on selected department
  filteredInstructors = signal<Instructor[]>([]);
  
  private instructorsService = inject(InstructorsService);
  private coursesService = inject(CoursesService);
  private ratingsService = inject(RatingsService);
  private router = inject(Router);

  ngOnInit(): void {
    this.instructorsService.getInstructors().subscribe(instructors => {
      this.instructors.set(instructors);
      this.updateFilteredInstructors();
    });
    this.coursesService.getCourses().subscribe(courses => {
      this.courses.set(courses);
    });
    this.updateRatings();
  }
  
  updateFilteredInstructors(): void {
    const department = this.selectedDepartment();
    let instructors: Instructor[];
    if (department === 'all') {
      instructors = this.instructors();
    } else {
      instructors = this.instructors().filter(inst => inst.department === department);
    }
    
    // Sort by last name alphabetically
    const sorted = [...instructors].sort((a, b) => {
      const aLastName = a.name.split(/\s+/).pop() || '';
      const bLastName = b.name.split(/\s+/).pop() || '';
      return aLastName.localeCompare(bLastName);
    });
    
    this.filteredInstructors.set(sorted);
  }

  selectInstructor(instructor: Instructor) {
    this.selectedInstructor.set(instructor);
    this.updateRatings();
  }

  selectInstructorById(id: string) {
    if (id === '') {
      this.selectedInstructor.set(null);
    } else {
      // Use filtered instructors to ensure we only select from the current department filter
      const instructor = this.filteredInstructors().find(i => i.id.toString() === id) ||
                         this.instructors().find(i => i.id.toString() === id);
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

  selectDepartment(department: string) {
    this.selectedDepartment.set(department);
    this.updateFilteredInstructors();
    // Clear selected instructor if it doesn't belong to the new department
    if (this.selectedInstructor()) {
      const deptInstructorIds = new Set(this.filteredInstructors().map(i => i.id));
      if (!deptInstructorIds.has(this.selectedInstructor()!.id)) {
        this.selectedInstructor.set(null);
      }
    }
    this.updateRatings();
  }

  clearFilters() {
    this.selectedInstructor.set(null);
    this.selectedCourse.set(null);
    this.selectedDepartment.set('all');
    this.updateFilteredInstructors();
    this.updateRatings();
  }

  updateRatings() {
    const instructorId = this.selectedInstructor()?.id;
    const courseId = this.selectedCourse()?.id;
    this.ratingsService.getRatings(instructorId?.toString(), courseId?.toString()).subscribe({
      next: ratings => {
        // Filter by department if selected
        let filteredRatings = ratings;
        const department = this.selectedDepartment();
        if (department !== 'all') {
          // Get all courses for the selected department
          const deptCourses = this.courses().filter(c => c.courseCode.startsWith(department));
          const deptCourseIds = new Set(deptCourses.map(c => c.id));
          
          // Get instructor IDs for the selected department (only from cs_professors_with_reviews.json or math_professors_with_reviews.json)
          const deptInstructorIds = new Set<number>();
          this.instructors().forEach(inst => {
            if (inst.department === department) {
              deptInstructorIds.add(inst.id);
            }
          });
          
          filteredRatings = ratings.filter(rating => {
            // RMP ratings: Only include if instructor belongs to the selected department
            if (rating.isRmpRating) {
              if (!rating.instructorId) return false;
              return deptInstructorIds.has(rating.instructorId);
            }
            // User-generated ratings: filter by course code or course ID
            if (rating.courseCode) {
              return rating.courseCode.startsWith(department);
            }
            if (rating.courseId && deptCourseIds.has(rating.courseId)) {
              return true;
            }
            // If no course code or course ID, exclude it
            return false;
          });
        }
        this.ratings.set(filteredRatings);
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

  openReviewsPage(instructorId: number) {
    this.router.navigate(['/instructors', instructorId, 'reviews']);
  }
}
