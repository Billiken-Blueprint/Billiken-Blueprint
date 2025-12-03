import { Component, inject, OnInit } from '@angular/core';
import { FormBuilder, FormControl, ReactiveFormsModule, Validators, FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Course, CoursesService } from '../services/courses-service/courses-service';
import { Select } from 'primeng/select';
import { MultiSelect } from 'primeng/multiselect';
import { UserInfoService } from '../services/user-info-service/user-info-service';
import { Router } from '@angular/router';
import { Degree, DegreesService } from '../services/degrees-service/degrees-service';
import { TimeSlot } from '../services/user-info-service/user-info-service';
import { forkJoin, of } from 'rxjs';
import { catchError } from 'rxjs/operators';

interface DegreeDisplayData extends Degree {
  displayLabel: string;
}

@Component({
  selector: 'app-questionnaire',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    Select,
    MultiSelect,
  ],
  templateUrl: './questionnaire.html',
  styleUrl: './questionnaire.css'

})
export class QuestionnairePage implements OnInit {
  // Multi-step navigation
  currentStep = 1;
  totalSteps = 4;
  courses: Course[] = [];
  degrees: DegreeDisplayData[] = [];
  private userInfoService = inject(UserInfoService);
  private degreesService = inject(DegreesService);
  private formBuilder = inject(FormBuilder);
  questionnaireForm = this.formBuilder.group({
    fullName: ['', Validators.required],
    graduationYear: ['', [Validators.required, Validators.min(2024), Validators.max(2030)]],
    major: new FormControl<DegreeDisplayData | null>(null, Validators.required),
    completedCourses: new FormControl([], []),
    unavailabilityTimes: new FormControl<TimeSlot[]>([], []),
    avoidTimes: new FormControl<TimeSlot[]>([], []),
  });
  private router = inject(Router);
  private coursesService = inject(CoursesService);


  ngOnInit(): void {
    forkJoin({
      courses: this.coursesService.getCourses(),
      degrees: this.degreesService.getDegrees(),
      userInfo: this.userInfoService.getUserInfo().pipe(
        catchError(() => of(null)) // Handle 404 or other errors gracefully
      )
    }).subscribe(({ courses, degrees, userInfo }) => {
      this.courses = courses;
      this.degrees = degrees.map(degree => ({
        ...degree,
        displayLabel: degree.name
      }));

      if (userInfo) {
        // Pre-populate form
        const selectedMajor = this.degrees.find(d => d.id === userInfo.degreeId);
        const selectedCourses = this.courses.filter(c => userInfo.completedCourseIds.includes(c.id));

        const unavailabilityTimes = (userInfo.unavailabilityTimes || []).map(t => ({
          day: t.day,
          start: this.convertHHMMToTime(t.start),
          end: this.convertHHMMToTime(t.end)
        }));

        const avoidTimes = (userInfo.avoidTimes || []).map(t => ({
          day: t.day,
          start: this.convertHHMMToTime(t.start),
          end: this.convertHHMMToTime(t.end)
        }));

        this.questionnaireForm.patchValue({
          fullName: userInfo.name,
          graduationYear: userInfo.graduationYear.toString(),
          major: selectedMajor,
          completedCourses: selectedCourses as any,
          unavailabilityTimes: unavailabilityTimes,
          avoidTimes: avoidTimes
        });
      }
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

    const unavailabilityTimes = (formValue.unavailabilityTimes || []).map(t => ({
      day: t.day,
      start: this.convertTimeToHHMM(t.start),
      end: this.convertTimeToHHMM(t.end)
    }));

    const avoidTimes = (formValue.avoidTimes || []).map(t => ({
      day: t.day,
      start: this.convertTimeToHHMM(t.start),
      end: this.convertTimeToHHMM(t.end)
    }));

    this.userInfoService.setUserInfo({
      name: profileData.fullName,
      graduationYear: profileData.graduationYear,
      degreeId: profileData.major!.id!,
      completedCourseIds: profileData.completedCourses?.map(x => x.id),
      unavailabilityTimes: unavailabilityTimes,
      avoidTimes: avoidTimes,
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

      case 3: // Schedule Preferences
        return true; // Optional step, always valid

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
        return 'Schedule Preferences';
      case 4:
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
        return 'Set your schedule preferences (optional)';
      case 4:
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
        return 'Schedule';
      case 4:
        return 'Review';
      default:
        return '';
    }
  }

  addUnavailabilityTime() {
    const current = this.questionnaireForm.get('unavailabilityTimes')?.value || [];
    this.questionnaireForm.patchValue({
      unavailabilityTimes: [...current, { day: 0, start: '09:00', end: '17:00' }]
    });
  }

  removeUnavailabilityTime(index: number) {
    const current = this.questionnaireForm.get('unavailabilityTimes')?.value || [];
    this.questionnaireForm.patchValue({
      unavailabilityTimes: current.filter((_, i) => i !== index)
    });
  }

  addAvoidTime() {
    const current = this.questionnaireForm.get('avoidTimes')?.value || [];
    this.questionnaireForm.patchValue({
      avoidTimes: [...current, { day: 0, start: '09:00', end: '17:00' }]
    });
  }

  removeAvoidTime(index: number) {
    const current = this.questionnaireForm.get('avoidTimes')?.value || [];
    this.questionnaireForm.patchValue({
      avoidTimes: current.filter((_, i) => i !== index)
    });
  }

  /**
   * Convert time format from HH:MM to HHMM for backend
   */
  convertTimeToHHMM(time: string): string {
    if (!time) return '0900';
    return time.replace(':', '');
  }

  /**
   * Convert time format from HHMM (backend) to HH:MM (frontend input)
   */
  convertHHMMToTime(hhmm: string): string {
    if (!hhmm || hhmm.length !== 4) return '09:00';
    return `${hhmm.substring(0, 2)}:${hhmm.substring(2, 4)}`;
  }
}
