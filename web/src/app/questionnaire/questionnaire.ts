import {Component, inject} from '@angular/core';
import {FormBuilder, ReactiveFormsModule, Validators, FormArray, FormControl} from '@angular/forms';
import {Router} from '@angular/router';
import {AuthService} from '../auth-service/auth-service';
import {CommonModule} from '@angular/common';
import {RouterLink} from '@angular/router';


interface Course {
  code: string;
  name: string;
  credits: number;
}

interface TimeSlot {
  time: string;
  label: string;
}

@Component({
  selector: 'app-questionnaire',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterLink
  ],
  templateUrl: './questionnaire.html',
  styleUrl: './questionnaire.css'
  
})
export class QuestionnairePage {
  private formBuilder = inject(FormBuilder);
  private router = inject(Router);
  private authService = inject(AuthService);

  // Multi-step navigation
  currentStep = 1;
  totalSteps = 5;

  courses: Course[] = [
    { code: 'CSCI 1300', name: 'Introduction to Object-Oriented Programming', credits: 4 },
    { code: 'CSCI 2100', name: 'Data Structures', credits: 4 },
    { code: 'CSCI 2300', name: 'Object-Oriented Software Design', credits: 3 },
    { code: 'CSCI 2500', name: 'Computer Organization and Systems', credits: 3 },
    { code: 'CSCI 2510', name: 'Principles of Computing Systems', credits: 3 },
    { code: 'CSCI 3100', name: 'Algorithms', credits: 3 },
    { code: 'CSCI 3200', name: 'Programming Languages', credits: 3 },
    { code: 'CSCI 3300', name: 'Software Engineering', credits: 3 },
    { code: 'CSCI 4961', name: 'Capstone Project I', credits: 2 },
    { code: 'CSCI 4962', name: 'Capstone Project II', credits: 2 }
  ];

  timeSlots: TimeSlot[] = [
    { time: '8:00-9:00', label: '8:00 AM - 9:00 AM' },
    { time: '9:00-10:00', label: '9:00 AM - 10:00 AM' },
    { time: '10:00-11:00', label: '10:00 AM - 11:00 AM' },
    { time: '11:00-12:00', label: '11:00 AM - 12:00 PM' },
    { time: '12:00-13:00', label: '12:00 PM - 1:00 PM' },
    { time: '13:00-14:00', label: '1:00 PM - 2:00 PM' },
    { time: '14:00-15:00', label: '2:00 PM - 3:00 PM' },
    { time: '15:00-16:00', label: '3:00 PM - 4:00 PM' },
    { time: '16:00-17:00', label: '4:00 PM - 5:00 PM' },
    { time: '17:00-18:00', label: '5:00 PM - 6:00 PM' },
    { time: '18:00-19:00', label: '6:00 PM - 7:00 PM' },
    { time: '19:00-20:00', label: '7:00 PM - 8:00 PM' },
    { time: '20:00-21:00', label: '8:00 PM - 9:00 PM' }
  ];

  majors = [
    'Computer Science',
    'Mathematics',
    'Engineering',
    'Business',
    'Biology',
    'Chemistry',
    'Physics',
    'English',
    'History',
    'Psychology',
    'Other'
  ];

  minors = [
    'None',
    'Computer Science',
    'Mathematics',
    'Business',
    'Biology',
    'Chemistry',
    'Physics',
    'English',
    'History',
    'Psychology',
    'Other'
  ];

  semesters = [
    'Freshman - Fall',
    'Freshman - Spring',
    'Sophomore - Fall',
    'Sophomore - Spring',
    'Junior - Fall',
    'Junior - Spring',
    'Senior - Fall',
    'Senior - Spring',
    'Graduate Student'
  ];

  questionnaireForm = this.formBuilder.group({
    fullName: ['', Validators.required],
    age: ['', [Validators.required, Validators.min(16), Validators.max(100)]],
    dateOfBirth: ['', Validators.required],
    graduationYear: ['', [Validators.required, Validators.min(2024), Validators.max(2030)]],
    currentSemester: [null, Validators.required],
    major: [null, Validators.required],
    minor: [''],
    completedCourses: this.formBuilder.array([]),
    unavailableTimes: this.formBuilder.array([]),
    unavailableReason: [''],
    preferredNotTimes: this.formBuilder.array([]),
    preferredNotReason: ['']
  });

  get completedCoursesArray() {
    return this.questionnaireForm.get('completedCourses') as FormArray;
  }

  get unavailableTimesArray() {
    return this.questionnaireForm.get('unavailableTimes') as FormArray;
  }

  get preferredNotTimesArray() {
    return this.questionnaireForm.get('preferredNotTimes') as FormArray;
  }

  constructor() {
    // Initialize course checkboxes
    this.courses.forEach(() => {
      this.completedCoursesArray.push(new FormControl(false));
    });

    // Initialize time slot checkboxes
    this.timeSlots.forEach(() => {
      this.unavailableTimesArray.push(new FormControl(false));
      this.preferredNotTimesArray.push(new FormControl(false));
    });
  }

  calculateTotalCredits(): number {
    let totalCredits = 0;
    this.completedCoursesArray.controls.forEach((control, index) => {
      if (control.value) {
        totalCredits += this.courses[index].credits;
      }
    });
    return totalCredits;
  }

  getTotalCredits(): number {
    return this.calculateTotalCredits();
  }

  getCourseSelectionCount(): number {
    return this.completedCoursesArray.controls.filter(control => control.value).length;
  }

  getUnavailableTimeControl(index: number): FormControl {
    return this.unavailableTimesArray.at(index) as FormControl;
  }

  getPreferredNotTimeControl(index: number): FormControl {
    return this.preferredNotTimesArray.at(index) as FormControl;
  }

  getSelectedCourses(): string[] {
    const selectedCourses: string[] = [];
    this.completedCoursesArray.controls.forEach((control, index) => {
      if (control.value) {
        selectedCourses.push(this.courses[index].code);
      }
    });
    return selectedCourses;
  }

  getSelectedUnavailableTimes(): string[] {
    const selectedTimes: string[] = [];
    this.unavailableTimesArray.controls.forEach((control, index) => {
      if (control.value) {
        selectedTimes.push(this.timeSlots[index].time);
      }
    });
    return selectedTimes;
  }

  getSelectedPreferredNotTimes(): string[] {
    const selectedTimes: string[] = [];
    this.preferredNotTimesArray.controls.forEach((control, index) => {
      if (control.value) {
        selectedTimes.push(this.timeSlots[index].time);
      }
    });
    return selectedTimes;
  }

  onSubmit() {
    if (this.questionnaireForm.valid) {
      const formValue = this.questionnaireForm.value;
      
      const profileData = {
        fullName: formValue.fullName || '',
        age: parseInt(formValue.age || '0'),
        dateOfBirth: formValue.dateOfBirth ? new Date(formValue.dateOfBirth) : undefined,
        graduationYear: parseInt(formValue.graduationYear || '0'),
        currentSemester: formValue.currentSemester || '',
        major: formValue.major || '',
        minor: formValue.minor || '',
        completedCourses: this.getSelectedCourses(),
        totalCredits: this.calculateTotalCredits(),
        unavailableTimes: this.getSelectedUnavailableTimes(),
        unavailableReason: formValue.unavailableReason || '',
        preferredNotTimes: this.getSelectedPreferredNotTimes(),
        preferredNotReason: formValue.preferredNotReason || '',
        questionnaireCompleted: true
      };

      // Save to auth service
      this.authService.updateProfile(profileData).subscribe({
        next: () => {
          this.router.navigate(['/']);
        },
        error: (error) => {
          console.error('Error saving profile:', error);
        }
      });
    }
  }

  selectAllCourses() {
    this.completedCoursesArray.controls.forEach(control => {
      control.setValue(true);
    });
  }

  deselectAllCourses() {
    this.completedCoursesArray.controls.forEach(control => {
      control.setValue(false);
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
      case 1: // Personal Information
        const personalControls = ['fullName', 'age', 'dateOfBirth', 'graduationYear'];
        const personalValid = personalControls.every(control => {
          const formControl = this.questionnaireForm.get(control);
          const isValid = formControl?.valid ?? false;
          console.log(`Step 1 - ${control}: value=${formControl?.value}, valid=${isValid}`);
          return isValid;
        });
        console.log('Step 1 overall valid:', personalValid);
        return personalValid;
      
      case 2: // Academic Information  
        const academicControls = ['currentSemester', 'major'];
        const academicValid = academicControls.every(control => {
          const formControl = this.questionnaireForm.get(control);
          const isValid = formControl?.valid ?? false;
          console.log(`Step 2 - ${control}: value=${formControl?.value}, valid=${isValid}, touched=${formControl?.touched}, dirty=${formControl?.dirty}`);
          return isValid;
        });
        console.log('Step 2 overall valid:', academicValid);
        return academicValid;
      
      case 3: // Course Selection
        return true; // Optional step
      
      case 4: // Time Preferences
        return true; // Optional step
      
      case 5: // Review
        return true; // Always allow viewing review
      
      default:
        return false;
    }
  }

  getStepTitle(): string {
    switch (this.currentStep) {
      case 1: return 'Personal Information';
      case 2: return 'Academic Information';
      case 3: return 'Course Selection';
      case 4: return 'Time Preferences';
      case 5: return 'Review & Submit';
      default: return '';
    }
  }
}