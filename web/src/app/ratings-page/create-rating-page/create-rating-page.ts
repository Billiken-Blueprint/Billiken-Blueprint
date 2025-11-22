import {Component, inject, OnInit, signal} from '@angular/core';
import {Select} from 'primeng/select';
import {Instructor, InstructorsService} from '../../instructors-service/instructors-service';
import {Course, CoursesService} from '../../courses-service/courses-service';
import {FormBuilder, FormControl, ReactiveFormsModule} from '@angular/forms';
import {Textarea} from 'primeng/textarea';
import {Rating} from 'primeng/rating';
import {RatingsService} from '../../ratings-service/ratings-service';
import {Router} from '@angular/router';
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
  form = this.formBuilder.group({
    instructor: new FormControl<Instructor | null | undefined>(null, []),
    course: new FormControl<Course | null | undefined>(null, []),
    instructorRating: new FormControl<number | null | undefined>(null, []),
    instructorDescription: new FormControl<string | null | undefined>(null, []),
    courseRating: new FormControl<number | null | undefined>(null, []),
    courseDescription: new FormControl<string | null | undefined>(null, []),
    bothRating: new FormControl<number | null | undefined>(null, []),
    bothDescription: new FormControl<string | null | undefined>(null, []),
  });
  private ratingsService = inject(RatingsService);

  submit() {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.errorMessage.set(null);
    const form = this.form.value;
    let completedRequests = 0;
    let totalRequests = 0;
    let hasError = false;

    if (form.instructor && form.instructorRating) {
      totalRequests++;
    }
    if (form.course && form.courseRating) {
      totalRequests++;
    }
    if (form.instructor && form.course && form.bothRating) {
      totalRequests++;
    }

    const checkComplete = () => {
      completedRequests++;
      if (completedRequests === totalRequests) {
        if (!hasError) {
          this.router.navigate(['/ratings']);
        }
      }
    };

    if (form.instructor && form.instructorRating) {
      this.ratingsService.createRating({
        instructorId: form.instructor.id.toString(),
        courseId: undefined,
        rating: form.instructorRating,
        description: form.instructorDescription ?? ""
      }).subscribe({
        next: () => checkComplete(),
        error: (error) => {
          console.error('Error creating instructor rating:', error);
          hasError = true;
          if (error.status === 400) {
            this.errorMessage.set('Unable to create rating. Please make sure you have completed your profile.');
          } else if (error.status === 401) {
            this.errorMessage.set('Please log in to create a rating.');
          } else {
            this.errorMessage.set('An error occurred while creating the rating. Please try again.');
          }
          checkComplete();
        }
      });
    }

    if (form.course && form.courseRating) {
      this.ratingsService.createRating({
        instructorId: undefined,
        courseId: form.course.id.toString(),
        rating: form.courseRating,
        description: form.courseDescription ?? ""
      }).subscribe({
        next: () => checkComplete(),
        error: (error) => {
          console.error('Error creating course rating:', error);
          hasError = true;
          if (error.status === 400) {
            this.errorMessage.set('Unable to create rating. Please make sure you have completed your profile.');
          } else if (error.status === 401) {
            this.errorMessage.set('Please log in to create a rating.');
          } else {
            this.errorMessage.set('An error occurred while creating the rating. Please try again.');
          }
          checkComplete();
        }
      });
    }

    if (form.instructor && form.course && form.bothRating) {
      this.ratingsService.createRating({
        instructorId: form.instructor.id.toString(),
        courseId: form.course.id.toString(),
        rating: form.bothRating,
        description: form.bothDescription ?? ""
      }).subscribe({
        next: () => checkComplete(),
        error: (error) => {
          console.error('Error creating combined rating:', error);
          hasError = true;
          if (error.status === 400) {
            this.errorMessage.set('Unable to create rating. Please make sure you have completed your profile.');
          } else if (error.status === 401) {
            this.errorMessage.set('Please log in to create a rating.');
          } else {
            this.errorMessage.set('An error occurred while creating the rating. Please try again.');
          }
          checkComplete();
        }
      });
    }
  }

  ngOnInit(): void {
    this.instructorsService.getInstructors().subscribe(this.instructors.set);
    this.coursesService.getCourses().subscribe(courses => {
      this.courses.set(courses.map(course => ({
        ...course,
        filterValue: `${course.courseCode} ${course.title}`,
        displayValue: `${course.courseCode} - (${course.title})`
      })));
    });
  }
}

interface FilterableCourse extends Course {
  filterValue: string;
  displayValue: string;
}
