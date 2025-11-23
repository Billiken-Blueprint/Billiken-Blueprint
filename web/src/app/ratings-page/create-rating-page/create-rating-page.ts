import {Component, computed, ElementRef, inject, OnInit, signal, ViewChild} from '@angular/core';
import {Select} from 'primeng/select';
import {Instructor, InstructorsService} from '../../instructors-service/instructors-service';
import {Course, CoursesService} from '../../courses-service/courses-service';
import {FormBuilder, FormControl, ReactiveFormsModule} from '@angular/forms';
import {Textarea} from 'primeng/textarea';
import {Rating} from 'primeng/rating';
import {RatingsService} from '../../ratings-service/ratings-service';
import {ActivatedRoute, Router} from '@angular/router';
import {CommonModule} from '@angular/common';

@Component({
  selector: 'app-create-rating-page',
  imports: [
    Select,
    ReactiveFormsModule,
    Textarea,
    Rating,
    CommonModule
  ],
  templateUrl: './create-rating-page.html',
  styleUrl: './create-rating-page.css',
  host: {
    class: 'block w-full min-h-screen'
  }
})
export class CreateRatingPage implements OnInit {
  instructors = signal<Instructor[]>([]);
  courses = signal<FilterableCourse[]>([]);
  errorMessage = signal<string | null>(null);
  private instructorsService = inject(InstructorsService);
  private coursesService = inject(CoursesService);
  private formBuilder = inject(FormBuilder);
  private router = inject(Router);
  private route = inject(ActivatedRoute);
  useNewInstructor = signal<boolean>(false);
  searchText = signal<string>('');
  instructorSearchText = signal<string>('');
  @ViewChild('instructorSelect') instructorSelect?: ElementRef;
  
  form = this.formBuilder.group({
    instructor: new FormControl<Instructor | null | undefined>(null, []),
    newInstructorName: new FormControl<string | null | undefined>(null, []),
    newInstructorDepartment: new FormControl<string | null | undefined>(null, []),
    course: new FormControl<Course | null | undefined>(null, []),
    rating: new FormControl<number | null | undefined>(null, []),
    description: new FormControl<string | null | undefined>(null, []),
    difficulty: new FormControl<number | null | undefined>(null, []),
    wouldTakeAgain: new FormControl<boolean | null | undefined>(null, []),
    grade: new FormControl<string | null | undefined>(null, []),
    attendance: new FormControl<string | null | undefined>(null, []),
  });
  private ratingsService = inject(RatingsService);

  submit() {
    // Don't block on form.invalid since we handle validation manually for new instructors
    // Just mark fields as touched for visual feedback
    this.form.markAllAsTouched();

    this.errorMessage.set(null);
    const form = this.form.value;
    
    // Validate that both instructor and course are selected
    if (!form.course) {
      this.errorMessage.set('Please select a course.');
      return;
    }
    
    if (!form.instructor && !(this.useNewInstructor() && form.newInstructorName)) {
      this.errorMessage.set('Please select or add a professor.');
      return;
    }
    
    if (!form.rating) {
      this.errorMessage.set('Please provide a rating.');
      return;
    }
    
    // Validate new instructor name and department if using new instructor
    if (this.useNewInstructor()) {
      if (!form.newInstructorName?.trim()) {
        this.errorMessage.set('Please enter a professor name.');
        return;
      }
      if (!form.newInstructorDepartment?.trim()) {
        this.errorMessage.set('Please select a department for the new professor.');
        return;
      }
    }
    
    // Track instructor ID for navigation
    let instructorIdForNavigation: number | null = null;
    if (form.instructor) {
      instructorIdForNavigation = form.instructor.id;
    }
    
    // Create single rating with both instructor and course
    this.ratingsService.createRating({
      instructorId: form.instructor ? form.instructor.id.toString() : undefined,
      instructorName: this.useNewInstructor() ? form.newInstructorName ?? undefined : undefined,
      instructorDepartment: this.useNewInstructor() ? form.newInstructorDepartment ?? undefined : undefined,
      courseId: form.course.id.toString(),
      rating: form.rating,
      description: form.description ?? "",
      difficulty: form.difficulty ?? null,
      wouldTakeAgain: form.wouldTakeAgain ?? null,
      grade: form.grade ?? null,
      attendance: form.attendance ?? null,
    }).subscribe({
      next: (response) => {
        console.log('Rating created successfully:', response);
        // If we created a new instructor, use the instructorId from the response for navigation
        if (this.useNewInstructor() && response.instructorId) {
          instructorIdForNavigation = response.instructorId;
        }
        
        // Navigate to instructor's reviews page
        if (instructorIdForNavigation) {
          console.log('Navigating to instructor reviews page:', instructorIdForNavigation);
          this.router.navigate(['/instructors', instructorIdForNavigation, 'reviews']).then(() => {
            console.log('Navigation successful');
          }).catch(err => {
            console.error('Navigation error:', err);
          });
        } else {
          console.log('Navigating to ratings page');
          this.router.navigate(['/ratings']);
        }
      },
      error: (error) => {
        console.error('Error creating rating:', error);
        if (error.status === 400) {
          this.errorMessage.set('Unable to create rating. Please make sure you have completed your profile.');
        } else if (error.status === 401) {
          this.errorMessage.set('Please log in to create a rating.');
        } else {
          this.errorMessage.set('An error occurred while creating the rating. Please try again.');
        }
      }
    });
  }

  ngOnInit(): void {
    this.instructorsService.getInstructors().subscribe(instructors => {
      this.instructors.set(instructors);
      
      // Check for instructorId query parameter and pre-select instructor
      this.route.queryParams.subscribe(params => {
        const instructorIdParam = params['instructorId'];
        if (instructorIdParam) {
          const instructorId = parseInt(instructorIdParam, 10);
          if (!isNaN(instructorId)) {
            const instructor = instructors.find(inst => inst.id === instructorId);
            if (instructor) {
              this.form.patchValue({ instructor });
            }
          }
        }
      });
    });
    
    this.coursesService.getCourses().subscribe(courses => {
      this.courses.set(courses.map(course => ({
        ...course,
        filterValue: `${course.courseCode} ${course.title}`,
        displayValue: `${course.courseCode} - (${course.title})`
      })));
    });
    
    // Track search text in the instructor select
    this.form.get('instructor')?.valueChanges.subscribe(() => {
      // Reset search text when instructor is selected
      this.instructorSearchText.set('');
      // If an instructor is selected, make sure we're not in "new instructor" mode
      if (this.form.get('instructor')?.value) {
        this.useNewInstructor.set(false);
      }
    });
  }
  
  getEmptyMessage(): string {
    return 'No professors found';
  }
  
  getFilteredInstructorsCount(): number {
    return this.filteredInstructors().length;
  }
  
  hasSearchText(): boolean {
    return this.instructorSearchText().trim().length > 0;
  }
  
  getSearchText(): string {
    return this.instructorSearchText();
  }
  
  onInstructorSearchChange(event: any): void {
    const value = event?.target?.value || '';
    this.instructorSearchText.set(value);
    // Clear selection if user starts typing again
    if (value && this.form.get('instructor')?.value) {
      this.form.patchValue({instructor: null});
    }
  }
  
  selectInstructor(instructor: Instructor): void {
    this.form.patchValue({instructor});
    this.instructorSearchText.set('');
  }
  
  filteredInstructors = computed(() => {
    const search = this.instructorSearchText().toLowerCase().trim();
    if (!search) return this.instructors();
    return this.instructors().filter(inst => 
      inst.name.toLowerCase().includes(search)
    );
  });

}

interface FilterableCourse extends Course {
  filterValue: string;
  displayValue: string;
}
