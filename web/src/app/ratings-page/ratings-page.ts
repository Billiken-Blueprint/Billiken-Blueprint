import {Component, inject, OnInit, signal, ViewEncapsulation} from '@angular/core';
import {Instructor, InstructorsService} from '../instructors-service/instructors-service';
import {DataView} from 'primeng/dataview';
import {Scroller} from 'primeng/scroller';
import {Card} from 'primeng/card';
import {InputText} from 'primeng/inputtext';
import {AutoComplete} from 'primeng/autocomplete';
import {Course, CoursesService} from '../courses-service/courses-service';
import {ButtonDirective} from 'primeng/button';
import {Rating, RatingsService} from '../ratings-service/ratings-service';
import {Toolbar} from 'primeng/toolbar';
import {CommonModule} from '@angular/common';

@Component({
  selector: 'app-ratings-page',
  imports: [
    Scroller,
    Card,
    ButtonDirective,
    Toolbar,
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
      }
    });
  }
}
