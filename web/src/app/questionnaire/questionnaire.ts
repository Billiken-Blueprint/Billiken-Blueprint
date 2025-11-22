import {Component, inject, OnInit} from '@angular/core';
import {FormBuilder, FormControl, ReactiveFormsModule, Validators} from '@angular/forms';
import {CommonModule} from '@angular/common';
import {Course, CoursesService} from '../services/courses-service/courses-service';
import {Select} from 'primeng/select';
import {MultiSelect} from 'primeng/multiselect';
import {UserInfoService} from '../services/user-info-service/user-info-service';
import {Router} from '@angular/router';
import {Degree, DegreesService} from '../services/degrees-service/degrees-service';

interface DegreeDisplayData extends Degree {
  displayLabel: string;
}

@Component({
  selector: 'app-questionnaire',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    Select,
    MultiSelect,
  ],
  templateUrl: './questionnaire.html',
  styleUrl: './questionnaire.css'

})
export class QuestionnairePage implements OnInit {
  // Multi-step navigation
  currentStep = 1;
  totalSteps = 3;
  courses: Course[] = [];
  degrees: DegreeDisplayData[] = [];
  private userInfoService = inject(UserInfoService);
  private degreesService = inject(DegreesService);
  private formBuilder = inject(FormBuilder);
  questionnaireForm = this.formBuilder.group({
    fullName: ['', Validators.required],
    graduationYear: ['', [Validators.required, Validators.min(2024), Validators.max(2030)]],
    major: [null, Validators.required],
    completedCourses: new FormControl([], []),
  });
  private router = inject(Router);
  private coursesService = inject(CoursesService);


  ngOnInit(): void {
    this.coursesService.getCourses().subscribe(courses => {
      this.courses = courses;
    });
    this.degreesService.getDegrees().subscribe(degrees => {
      this.degrees = degrees.map(degree => ({
        ...degree,
        displayLabel: `${degree.degreeType} ${degree.major} (${degree.college})`
      }));
    });
  }


  onSubmit() {
    if (this.questionnaireForm.invalid) {
      this.questionnaireForm.markAllAsTouched();
      return;
    }
    const formValue = this.questionnaireForm.value;

    const profileData = {
      fullName: formValue.fullName || '',
      graduationYear: parseInt(formValue.graduationYear || '0'),
      major: formValue.major,
      completedCourses: formValue.completedCourses as Course[],
      questionnaireCompleted: true
    };

    this.userInfoService.updateUserInfo({
      name: profileData.fullName,
      graduationYear: profileData.graduationYear,
      major: profileData.major!,
      completedCourseIds: profileData.completedCourses?.map(x => x.id)
    }).subscribe({
      next: () => {
        this.router.navigate(['/home']);
      }
    });
  }

  // Multi-step navigation methods
  nextStep() {
    if (this.currentStep < this.totalSteps && this.isCurrentStepValid()) {
      this.currentStep++;
    }
  }

  previousStep() {
    if (this.currentStep > 1) {
      this.currentStep--;
    }
  }

  goToStep(step: number) {
    if (step >= 1 && step <= this.totalSteps) {
      this.currentStep = step;
    }
  }

  isCurrentStepValid(): boolean {
    switch (this.currentStep) {
      case 1: // Student Information
        const personalControls = ['fullName', 'graduationYear', 'major'];
        return personalControls.every(control => {
          const formControl = this.questionnaireForm.get(control);
          return formControl?.valid ?? false;
        });

      case 2: // Previous Courses
        const previousCoursesControls = ['completedCourses'];
        return previousCoursesControls.every(control => {
          const formControl = this.questionnaireForm.get(control);
          return formControl?.valid ?? false;
        });

      default:
        return false;
    }
  }

  getStepTitle(): string {
    switch (this.currentStep) {
      case 1:
        return 'Student Information';
      case 2:
        return 'Previous Courses';
      case 3:
        return 'Review & Submit';
      default:
        return '';
    }
  }

  getStepDescription(): string {
    switch (this.currentStep) {
      case 1:
        return 'Tell us about yourself and your academic goals';
      case 2:
        return 'Help us understand your current progress';
      case 3:
        return 'Review your information before completing your profile';
      default:
        return '';
    }
  }

  getStepLabel(step: number): string {
    switch (step) {
      case 1:
        return 'Personal Info';
      case 2:
        return 'Courses';
      case 3:
        return 'Review';
      default:
        return '';
    }
  }
}
