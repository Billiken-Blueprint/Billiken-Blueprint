import {Component, inject, OnInit} from '@angular/core';
import {FormBuilder, FormControl, ReactiveFormsModule, Validators} from '@angular/forms';
import {CommonModule} from '@angular/common';
import {Course, CoursesService} from '../courses-service/courses-service';
import {Select} from 'primeng/select';
import {MultiSelect} from 'primeng/multiselect';
import {UserInfoService} from '../user-info-service/user-info-service';
import {Router} from '@angular/router';


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
  majors = [
    'Computer Science',
  ];
  minors = [
    'Computer Science',
  ];
  private userInfoService = inject(UserInfoService);
  private formBuilder = inject(FormBuilder);
  questionnaireForm = this.formBuilder.group({
    fullName: ['', Validators.required],
    graduationYear: ['', [Validators.required, Validators.min(2024), Validators.max(2030)]],
    major: [null, Validators.required],
    minor: [''],
    completedCourses: new FormControl([], []),
  });
  private router = inject(Router);
  private coursesService = inject(CoursesService);


  ngOnInit(): void {
    this.coursesService.getCourses().subscribe(courses => {
      this.courses = courses;
    })
  }


  onSubmit() {
    console.log(this.questionnaireForm.valid)
    if (this.questionnaireForm.invalid) {
      this.questionnaireForm.markAllAsTouched();
      return;
    }
    const formValue = this.questionnaireForm.value;

    const profileData = {
      fullName: formValue.fullName || '',
      graduationYear: parseInt(formValue.graduationYear || '0'),
      major: formValue.major || '',
      minor: formValue.minor || '',
      completedCourses: formValue.completedCourses as Course[],
      questionnaireCompleted: true
    };

    const completedCourseIds = profileData.completedCourses?.map(x => x.id).filter(id => id !== undefined) || [];
    
    this.userInfoService.updateUserInfo({
      name: profileData.fullName,
      graduationYear: profileData.graduationYear,
      major: profileData.major,
      minor: profileData.minor || null,
      completedCourseIds: completedCourseIds
    }).subscribe({
      next: () => {
        this.router.navigate(['/home']);
      },
      error: (error) => {
        console.error('Error submitting profile:', error);
        alert('Failed to save profile. Please try again. If the problem persists, please contact support.');
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
        const personalControls = ['fullName', 'graduationYear', 'major', 'minor'];
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
