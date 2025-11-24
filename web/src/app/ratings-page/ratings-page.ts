import {Component, computed, inject, OnInit, signal, ViewEncapsulation} from '@angular/core';
import {Instructor, InstructorsService, RmpReview} from '../instructors-service/instructors-service';
import {Course, CoursesService} from '../courses-service/courses-service';
import {Rating, RatingsService} from '../ratings-service/ratings-service';
import {CommonModule} from '@angular/common';
import {Router} from '@angular/router';
import {forkJoin, of, Observable} from 'rxjs';
import {catchError} from 'rxjs/operators';

// Import course data from courses page
type GroupKey =
  | 'Core_Intro'
  | 'Core_Prog'
  | 'Core_Software'
  | 'Core_Systems'
  | 'Stem_MathCore'
  | 'Stem_MathAdv'
  | 'Stem_Science'
  | 'Stem_Ethics'
  | 'Electives_Systems'
  | 'Electives_AIData'
  | 'Electives_Software'
  | 'Electives_Capstone';

interface SimpleCourse {
  code: string;
  title: string;
}

const COURSE_GROUP_DATA: Record<GroupKey, SimpleCourse[]> = {
  Core_Intro: [
    { code: 'CSCI 1010', title: 'Introduction to Computer Science: Principles' },
    { code: 'CSCI 1020', title: 'Introduction to Computer Science: Bioinformatics' },
    { code: 'CSCI 1025', title: 'Introduction to Computer Science: Cybersecurity' },
    { code: 'CSCI 1030', title: 'Introduction to Computer Science: Game Design' },
    { code: 'CSCI 1040', title: 'Introduction to Computer Science: Mobile Computing' },
    { code: 'CSCI 1050', title: 'Introduction to Computer Science: Multimedia' },
    { code: 'CSCI 1060', title: 'Introduction to Computer Science: Scientific Programming' },
    { code: 'CSCI 1070', title: 'Introduction to Computer Science: Taming Big Data' },
    { code: 'CSCI 1080', title: 'Introduction to Computer Science: World Wide Web' },
    { code: 'CSCI 1090', title: 'Introduction to Computer Science: Special Topics' }
  ],
  Core_Prog: [
    { code: 'CSCI 1300', title: 'Introduction to Object-Oriented Programming' },
    { code: 'CSCI 2100', title: 'Data Structures' },
    { code: 'CSCI 2190', title: 'Computational Problem Solving' },
    { code: 'CSCI 2300', title: 'Object-Oriented Software Design' },
    { code: 'CSCI 3100', title: 'Algorithms' },
    { code: 'CSCI 3200', title: 'Programming Languages' },
    { code: 'CSCI 3250', title: 'Compilers' },
    { code: 'CSCI 3300', title: 'Software Engineering' }
  ],
  Core_Software: [
    { code: 'CSCI 3710', title: 'Databases' },
    { code: 'CSCI 3810', title: 'Game Programming' },
    { code: 'CSCI 4120', title: 'Advanced Data Structures' },
    { code: 'CSCI 4310', title: 'Software Architecture' },
    { code: 'CSCI 4340', title: 'Safety-Critical Software Systems' },
    { code: 'CSCI 4355', title: 'Human Computer Interaction' },
    { code: 'CSCI 4360', title: 'Web Technologies' },
    { code: 'CSCI 4370', title: 'User Interface Design' },
    { code: 'CSCI 4380', title: 'DevOps' }
  ],
  Core_Systems: [
    { code: 'CSCI 2500', title: 'Computer Organization and Systems' },
    { code: 'CSCI 2510', title: 'Principles of Computing Systems' },
    { code: 'CSCI 3450X', title: 'Microprocessors' },
    { code: 'CSCI 3451X', title: 'Microprocessors Laboratory' },
    { code: 'CSCI 4500', title: 'Operating Systems' },
    { code: 'CSCI 4520', title: 'Internet of Things' },
    { code: 'CSCI 4590', title: 'Wireless Sensor Networks' },
    { code: 'CSCI 4610', title: 'Concurrent and Parallel Programming' },
    { code: 'CSCI 4620', title: 'Distributed Computing' }
  ],
  Stem_MathCore: [
    { code: 'MATH 1510', title: 'Calculus I' },
    { code: 'MATH 1520', title: 'Calculus II' },
    { code: 'MATH 1660', title: 'Discrete Mathematics' },
    { code: 'STAT 3850', title: 'Foundation of Statistics' }
  ],
  Stem_MathAdv: [
    { code: 'MATH 2530', title: 'Calculus III (example advanced math)' },
    { code: 'MATH 3110', title: 'Linear Algebra (example)' },
    { code: 'MATH 3120', title: 'Advanced Linear Algebra (example)' },
    { code: 'STAT 4000', title: 'Advanced Statistics (example)' },
    { code: 'MATH 3730', title: 'Numerical Methods (example)' },
    { code: 'MATH 4100', title: 'Advanced Topics in Math (example)' },
    { code: 'STAT 4100', title: 'Applied Statistics (example)' },
    { code: 'STAT 4200', title: 'Probability and Statistics (example)' }
  ],
  Stem_Science: [
    { code: 'PHYS 1310', title: 'Physics I with Lab (example)' },
    { code: 'PHYS 1320', title: 'Physics II with Lab (example)' },
    { code: 'CHEM 1110', title: 'General Chemistry I with Lab (example)' },
    { code: 'CHEM 1120', title: 'General Chemistry II with Lab (example)' },
    { code: 'BIOL 1240', title: 'Principles of Biology I with Lab (example)' },
    { code: 'BME 2000', title: 'Biomedical Engineering Computing' },
    { code: 'CVNG 1500', title: 'Civil Engineering Computing' },
    { code: 'SCI 2000', title: 'Science/Engineering Elective (example)' }
  ],
  Stem_Ethics: [
    { code: 'PHIL 3050X', title: 'Computer Ethics' },
    { code: 'CSCI 3050', title: 'Computer Ethics (CSCI listing)' },
    { code: 'PHIL 2050', title: 'Ethics (example prerequisite)' },
    { code: 'PHIL 3000', title: 'Advanced Ethics & Technology (example)' }
  ],
  Electives_Systems: [
    { code: 'CSCI 4500', title: 'Operating Systems' },
    { code: 'CSCI 4520', title: 'Internet of Things' },
    { code: 'CSCI 4530', title: 'Computer Security' },
    { code: 'CSCI 4550', title: 'Computer Networks' },
    { code: 'CSCI 4590', title: 'Wireless Sensor Networks' },
    { code: 'CSCI 4610', title: 'Concurrent and Parallel Programming' },
    { code: 'CSCI 4620', title: 'Distributed Computing' },
    { code: 'CSCI 4870', title: 'Applied Cryptography' }
  ],
  Electives_AIData: [
    { code: 'CSCI 4710', title: 'Databases' },
    { code: 'CSCI 4740', title: 'Artificial Intelligence' },
    { code: 'CSCI 4750', title: 'Machine Learning' },
    { code: 'CSCI 4756', title: 'Applied Machine Learning' },
    { code: 'CSCI 4760', title: 'Deep Learning' },
    { code: 'CSCI 4770', title: 'Big Data Analytics' },
    { code: 'CSCI 4780', title: 'Data Engineering' },
    { code: 'CSCI 4830', title: 'Computer Vision' },
    { code: 'CSCI 4845', title: 'Natural Language Processing' }
  ],
  Electives_Software: [
    { code: 'CSCI 3710', title: 'Databases' },
    { code: 'CSCI 3810', title: 'Game Programming' },
    { code: 'CSCI 4310', title: 'Software Architecture' },
    { code: 'CSCI 4355', title: 'Human Computer Interaction' },
    { code: 'CSCI 4360', title: 'Web Technologies' },
    { code: 'CSCI 4370', title: 'User Interface Design' },
    { code: 'CSCI 4380', title: 'DevOps' },
    { code: 'CSCI 4820', title: 'Computer Graphics' },
    { code: 'CSCI 4860', title: 'Autonomous Driving' }
  ],
  Electives_Capstone: [
    { code: 'CSCI 3910', title: 'Internship with Industry' },
    { code: 'CSCI 4910', title: 'Internship with Industry (Advanced)' },
    { code: 'CSCI 4930', title: 'Special Topics' },
    { code: 'CSCI 4961', title: 'Capstone Project I' },
    { code: 'CSCI 4962', title: 'Capstone Project II' },
    { code: 'CSCI 4980', title: 'Advanced Independent Study' },
    { code: 'CSCI 1930', title: 'Special Topics (Lower Division)' },
    { code: 'CSCI 1980', title: 'Independent Study (Lower Division)' },
    { code: 'CSCI 2930', title: 'Special Topics (Middle Division)' },
    { code: 'CSCI 2980', title: 'Independent Study (Middle Division)' },
    { code: 'CSCI 3930', title: 'Special Topics (Upper Division)' },
    { code: 'CSCI 3980', title: 'Independent Study (Upper Division)' }
  ]
};

// Flatten all courses from all groups
function getAllCoursesFromCoursePage(): Course[] {
  const allCourses: Course[] = [];
  let id = 1;
  for (const group of Object.values(COURSE_GROUP_DATA)) {
    for (const course of group) {
      allCourses.push({
        id: id++,
        courseCode: course.code,
        title: course.title
      });
    }
  }
  return allCourses;
}

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
  
  // Search text for filtering
  instructorSearchText = signal<string>('');
  courseSearchText = signal<string>('');
  
  // Track focus state
  instructorInputFocused = signal<boolean>(false);
  courseInputFocused = signal<boolean>(false);
  
  // Get filtered instructors based on selected department
  filteredInstructors = signal<Instructor[]>([]);
  
  // Computed filtered lists for search
  searchFilteredInstructors = computed(() => {
    const search = this.instructorSearchText().toLowerCase().trim();
    const deptFiltered = this.filteredInstructors();
    if (!search) {
      // Show all instructors when no search text
      return deptFiltered;
    }
    return deptFiltered.filter(inst => 
      inst.name.toLowerCase().includes(search)
    );
  });
  
  searchFilteredCourses = computed(() => {
    const search = this.courseSearchText().toLowerCase().trim();
    const allCourses = this.courses();
    if (!search) {
      // Show all courses when no search text
      return allCourses;
    }
    return allCourses.filter(course => 
      course.courseCode.toLowerCase().includes(search) ||
      course.title.toLowerCase().includes(search)
    );
  });
  
  // Group ratings by instructor for display (as array for template iteration)
  groupedRatings = signal<Array<[number, { instructor: Instructor | null; rmpRating: Rating | null; bbRatings: Rating[]; combined: { average: number; bbCount: number; rmpRating: number | null } | null }]>>([]);
  
  // Individual reviews for course view
  individualReviews = signal<RmpReview[]>([]);
  loadingReviews = signal<boolean>(false);
  
  // Group individual reviews by instructor
  groupedIndividualReviews = computed(() => {
    const reviews = this.individualReviews();
    if (reviews.length === 0) {
      return [];
    }
    
    const grouped = new Map<number, RmpReview[]>();
    
    reviews.forEach(review => {
      const instructorId = review.instructorId;
      if (!grouped.has(instructorId)) {
        grouped.set(instructorId, []);
      }
      grouped.get(instructorId)!.push(review);
    });
    
    // Convert to array, calculate average rating, and sort by average (high to low)
    const groupedArray = Array.from(grouped.entries()).map(([instructorId, reviews]) => {
      const instructor = this.instructors().find(i => i.id === instructorId);
      
      // Calculate average rating - ensure quality is a valid number
      const validReviews = reviews.filter(r => r.quality != null && !isNaN(r.quality));
      const totalRating = validReviews.reduce((sum, review) => sum + (review.quality || 0), 0);
      const averageRating = validReviews.length > 0 ? totalRating / validReviews.length : 0;
      
      return {
        instructorId,
        instructorName: instructor?.name || 'Unknown Instructor',
        averageRating,
        reviews: [...reviews].sort((a, b) => {
          // Sort by date (newest first)
          if (a.reviewDate && b.reviewDate) {
            return new Date(b.reviewDate).getTime() - new Date(a.reviewDate).getTime();
          }
          if (a.reviewDate && !b.reviewDate) return -1;
          if (!a.reviewDate && b.reviewDate) return 1;
          return (b.id || 0) - (a.id || 0);
        })
      };
    });
    
    // Sort by average rating (high to low) - ensure stable sort
    return groupedArray.sort((a, b) => {
      const diff = b.averageRating - a.averageRating;
      // If averages are equal, sort by number of reviews (more reviews first)
      if (Math.abs(diff) < 0.01) {
        return b.reviews.length - a.reviews.length;
      }
      return diff;
    });
  });
  
  private instructorsService = inject(InstructorsService);
  private coursesService = inject(CoursesService);
  private ratingsService = inject(RatingsService);
  private router = inject(Router);

  ngOnInit(): void {
    this.instructorsService.getInstructors().subscribe(instructors => {
      this.instructors.set(instructors);
      this.updateFilteredInstructors();
    });
    
    // Get courses from API and merge with courses page data
    this.coursesService.getCourses().subscribe(apiCourses => {
      // Get all courses from courses page
      const coursesPageCourses = getAllCoursesFromCoursePage();
      
      // Create a map of existing courses by courseCode to avoid duplicates
      const courseMap = new Map<string, Course>();
      
      // Add API courses first (they have database IDs)
      for (const course of apiCourses) {
        courseMap.set(course.courseCode, course);
      }
      
      // Add courses page courses (only if not already in map)
      for (const course of coursesPageCourses) {
        if (!courseMap.has(course.courseCode)) {
          courseMap.set(course.courseCode, course);
        }
      }
      
      // Convert map to array and sort by course code
      const allCourses = Array.from(courseMap.values()).sort((a, b) => 
        a.courseCode.localeCompare(b.courseCode)
      );
      
      this.courses.set(allCourses);
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

  onInstructorSearchChange(event: any): void {
    const value = event?.target?.value || '';
    this.instructorSearchText.set(value);
    // Clear selection if user starts typing again
    if (value && this.selectedInstructor()) {
      this.selectedInstructor.set(null);
    }
  }
  
  onInstructorFocus(): void {
    this.instructorInputFocused.set(true);
  }
  
  onInstructorBlur(): void {
    // Delay to allow click events to fire first
    setTimeout(() => {
      this.instructorInputFocused.set(false);
    }, 200);
  }
  
  selectInstructorFromSearch(instructor: Instructor): void {
    this.selectedInstructor.set(instructor);
    this.instructorSearchText.set(''); // Clear search text
    this.instructorInputFocused.set(false); // Hide dropdown
    this.updateRatings();
  }
  
  onCourseSearchChange(event: any): void {
    const value = event?.target?.value || '';
    this.courseSearchText.set(value);
    // Clear selection if user starts typing again
    if (value && this.selectedCourse()) {
      this.selectedCourse.set(null);
    }
  }
  
  onCourseFocus(): void {
    this.courseInputFocused.set(true);
  }
  
  onCourseBlur(): void {
    // Delay to allow click events to fire first
    setTimeout(() => {
      this.courseInputFocused.set(false);
    }, 200);
  }
  
  selectCourseFromSearch(course: Course): void {
    this.selectedCourse.set(course);
    this.courseSearchText.set(''); // Clear search text
    this.courseInputFocused.set(false); // Hide dropdown
    this.updateRatings();
  }
  
  clearInstructorSelection(): void {
    this.selectedInstructor.set(null);
    this.instructorSearchText.set('');
    this.instructorInputFocused.set(false);
    this.updateRatings();
  }
  
  clearCourseSelection(): void {
    this.selectedCourse.set(null);
    this.courseSearchText.set('');
    this.courseInputFocused.set(false);
    this.updateRatings();
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
    this.instructorSearchText.set('');
    this.courseSearchText.set('');
    this.instructorInputFocused.set(false);
    this.courseInputFocused.set(false);
    this.updateFilteredInstructors();
    this.updateRatings();
  }

  updateRatings() {
    const instructorId = this.selectedInstructor()?.id;
    const courseId = this.selectedCourse()?.id;
    
    // If course is selected but no instructor, show individual reviews
    if (courseId && !instructorId) {
      this.loadIndividualReviewsForCourse(courseId);
      return;
    }
    
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
        
        // Additional client-side filtering by course if selected (in case backend doesn't filter correctly)
        if (courseId) {
          filteredRatings = filteredRatings.filter(rating => {
            // Check courseId first (most reliable)
            if (rating.courseId === courseId) {
              return true;
            }
            // Fallback: check courseCode
            if (rating.courseCode) {
              const selectedCourse = this.selectedCourse();
              if (selectedCourse) {
                return rating.courseCode === selectedCourse.courseCode;
              }
            }
            // For RMP ratings without courseId, we can't filter client-side reliably
            // The backend should have filtered these
            return false;
          });
        }
        
        this.ratings.set(filteredRatings);
        this.updateGroupedRatings(filteredRatings);
        // Clear individual reviews when showing grouped view
        this.individualReviews.set([]);
      },
      error: (error) => {
        console.error('Error loading ratings:', error);
        // Set empty array on error to prevent UI issues
        this.ratings.set([]);
        this.groupedRatings.set([]);
        this.individualReviews.set([]);
      }
    });
  }
  
  loadIndividualReviewsForCourse(courseId: number): void {
    this.loadingReviews.set(true);
    const course = this.courses().find(c => c.id === courseId);
    if (!course) {
      console.error(`Course with id ${courseId} not found`);
      this.loadingReviews.set(false);
      return;
    }
    
    const normalizedCourseCode = course.courseCode.replace(/\s+/g, '').replace(/-/g, '').toUpperCase();
    console.log(`Loading reviews for course: ${course.courseCode} (normalized: ${normalizedCourseCode})`);
    
    // Get all instructors who have ratings for this course
    // This includes both BB ratings and RMP ratings that match the course
    this.ratingsService.getRatings(null, courseId.toString()).subscribe({
      next: ratings => {
        console.log(`Found ${ratings.length} ratings for course ${course.courseCode}`);
        const instructorIds = new Set<number>();
        const filteredReviews: RmpReview[] = [];
        
        // First, convert BB ratings from the API response to RmpReview format
        // Also track which instructors have ratings for this course (including RMP ratings)
        const instructorsWithCourseRatings = new Set<number>();
        
        ratings.forEach(rating => {
          if (rating.instructorId) {
            instructorIds.add(rating.instructorId);
            // Track instructors who have any rating (BB or RMP) for this course
            // RMP ratings from API have courseId set when filtering by course
            if (rating.courseId === courseId) {
              instructorsWithCourseRatings.add(rating.instructorId);
              console.log(`Instructor ${rating.instructorId} has rating for course ${course.courseCode} (isRmpRating: ${rating.isRmpRating})`);
            }
            // Also track RMP ratings even if courseId doesn't match (they're included by backend for this course)
            if (rating.isRmpRating && rating.courseId === courseId) {
              instructorsWithCourseRatings.add(rating.instructorId);
            }
          }
          
          // Include BB ratings directly (they already have courseId matching from backend)
          if (!rating.isRmpRating && rating.courseId === courseId) {
            filteredReviews.push({
              id: rating.id!,
              type: 'billiken_blueprint',
              instructorId: rating.instructorId!,
              courseCode: rating.courseCode || null,
              courseName: rating.courseName || null,
              courseId: rating.courseId || null,
              quality: rating.rating,
              comment: rating.description || '',
              reviewDate: rating.createdAt || null,
              difficulty: rating.difficulty || null,
              wouldTakeAgain: rating.wouldTakeAgain || null,
              grade: rating.grade || null,
              attendance: rating.attendance || null,
              tags: [],
              canDelete: rating.canEdit || false,
            });
            console.log(`Added BB rating: ${rating.id} for course ${course.courseCode}`);
          }
          // Note: RMP ratings from API are summary ratings, not individual reviews
          // We'll fetch individual RMP reviews below
        });
        
        console.log(`Instructors with course ratings: ${Array.from(instructorsWithCourseRatings).join(', ')}`);
        
        // Only fetch from instructors who have ratings for this course
        // Reviews without course_id will be filtered out, but that's correct - they need to be updated
        console.log(`Will fetch RMP reviews from ${instructorIds.size} instructors for course ${course.courseCode}`);
        
        if (instructorIds.size === 0) {
          // No instructors to fetch RMP reviews from, but we might have BB ratings already
          console.log(`No instructors to fetch RMP reviews from. Total reviews so far: ${filteredReviews.length}`);
          // Sort and set reviews
          filteredReviews.sort((a, b) => {
            if (a.reviewDate && b.reviewDate) {
              return new Date(b.reviewDate).getTime() - new Date(a.reviewDate).getTime();
            }
            if (a.reviewDate && !b.reviewDate) return -1;
            if (!a.reviewDate && b.reviewDate) return 1;
            const aId = a.id || 0;
            const bId = b.id || 0;
            return bId - aId;
          });
          this.individualReviews.set(filteredReviews);
          this.loadingReviews.set(false);
          return;
        }
        
        // Fetch individual reviews for each instructor using forkJoin (for RMP reviews)
        const reviewObservables: Observable<RmpReview[]>[] = Array.from(instructorIds).map(id =>
          this.instructorsService.getInstructorReviews(id).pipe(
            catchError(err => {
              console.error(`Error loading reviews for instructor ${id}:`, err);
              return of<RmpReview[]>([]);
            })
          )
        );
        
        forkJoin(reviewObservables).subscribe({
          next: (allReviews) => {
            console.log(`Received reviews from ${allReviews.length} instructors`);
            // Flatten and filter reviews for this course
            // Only add RMP reviews (BB ratings already added above)
            
            allReviews.forEach((reviews, index) => {
              const instructorId = Array.from(instructorIds)[index];
              const instructorHasCourseRating = instructorsWithCourseRatings.has(instructorId);
              console.log(`Processing ${reviews.length} reviews from instructor ${instructorId} (has course rating: ${instructorHasCourseRating})`);
              
              reviews.forEach(review => {
                // Only add RMP reviews (BB ratings already added from API response)
                if (review.type === 'rmp') {
                  let matches = false;
                  
                  // Priority 1: Match by courseId (most reliable)
                  if (review.courseId === courseId) {
                    matches = true;
                    console.log(`Matched RMP review by courseId: ${review.type} review ${review.id} for course ${course.courseCode}`);
                  } 
                  // Priority 2: Match by course code string if courseId is not available
                  else if (!review.courseId && (review.course || review.courseCode)) {
                    const reviewCourseCode = (review.courseCode || review.course || '').replace(/\s+/g, '').replace(/-/g, '').toUpperCase();
                    if (reviewCourseCode && normalizedCourseCode && 
                        (reviewCourseCode.includes(normalizedCourseCode) || normalizedCourseCode.includes(reviewCourseCode))) {
                      matches = true;
                      console.log(`Matched RMP review by course code: ${review.type} review ${review.id} (${review.course || review.courseCode}) for course ${course.courseCode}`);
                    }
                  }
                  // Priority 3: If review has no course info, only include if instructor has a rating for this course
                  // This handles legacy RMP reviews that haven't been updated with course_id yet
                  else if (!review.courseId && !review.course && !review.courseCode && instructorHasCourseRating) {
                    matches = true;
                    console.log(`Including RMP review without course info: ${review.type} review ${review.id} (instructor ${instructorId} has rating for course ${course.courseCode})`);
                  }
                  
                  if (matches) {
                    filteredReviews.push(review);
                  } else {
                    // Log why review was rejected
                    if (review.courseId !== null && review.courseId !== undefined) {
                      console.log(`Rejected review: ${review.type} review ${review.id} has courseId ${review.courseId}, expected ${courseId}`);
                    } else if (review.course || review.courseCode) {
                      console.log(`Rejected review: ${review.type} review ${review.id} has course code that doesn't match (course: ${review.course || review.courseCode || 'none'})`);
                    } else {
                      console.log(`Rejected review: ${review.type} review ${review.id} has no course info and instructor doesn't have rating for course ${course.courseCode}`);
                    }
                  }
                }
              });
            });
            
            // Sort by date (newest first)
            filteredReviews.sort((a, b) => {
              if (a.reviewDate && b.reviewDate) {
                return new Date(b.reviewDate).getTime() - new Date(a.reviewDate).getTime();
              }
              if (a.reviewDate && !b.reviewDate) return -1;
              if (!a.reviewDate && b.reviewDate) return 1;
              const aId = a.id || 0;
              const bId = b.id || 0;
              return bId - aId;
            });
            
            console.log(`Filtered to ${filteredReviews.length} reviews for course ${course.courseCode}`);
            this.individualReviews.set(filteredReviews);
            this.loadingReviews.set(false);
          },
          error: (err) => {
            console.error('Error loading individual reviews:', err);
            this.individualReviews.set([]);
            this.loadingReviews.set(false);
          }
        });
      },
      error: (err) => {
        console.error('Error loading ratings for course:', err);
        this.individualReviews.set([]);
        this.loadingReviews.set(false);
      }
    });
  }
  
  formatDate(dateString: string | null): string {
    if (!dateString) return '';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    } catch {
      return dateString;
    }
  }
  
  getReviewDate(review: RmpReview): string | null {
    if (review.reviewDate) {
      return this.formatDate(review.reviewDate);
    }
    return null;
  }
  
  getInstructorName(instructorId: number): string {
    const instructor = this.instructors().find(i => i.id === instructorId);
    return instructor?.name || 'Unknown Instructor';
  }
  
  updateGroupedRatings(ratings: Rating[]): void {
    const grouped = new Map<number, { instructor: Instructor | null; rmpRating: Rating | null; bbRatings: Rating[]; combined: { average: number; bbCount: number; rmpRating: number | null } | null }>();
    
    // Group ratings by instructor
    for (const rating of ratings) {
      if (!rating.instructorId) continue;
      
      if (!grouped.has(rating.instructorId)) {
        const instructor = this.instructors().find(i => i.id === rating.instructorId) || null;
        grouped.set(rating.instructorId, {
          instructor,
          rmpRating: null,
          bbRatings: [],
          combined: null
        });
      }
      
      const group = grouped.get(rating.instructorId)!;
      if (rating.isRmpRating) {
        group.rmpRating = rating;
      } else {
        group.bbRatings.push(rating);
      }
    }
    
    // Calculate combined ratings for each group
    for (const [instructorId, group] of grouped.entries()) {
      group.combined = this.calculateCombinedRatingForGroup(group);
    }
    
    // Convert Map to array for template iteration
    const groupedArray = Array.from(grouped.entries());
    console.log('Grouped ratings:', groupedArray.length, 'instructors from', ratings.length, 'ratings');
    this.groupedRatings.set(groupedArray);
  }
  
  calculateCombinedRatingForGroup(group: { instructor: Instructor | null; rmpRating: Rating | null; bbRatings: Rating[]; combined: { average: number; bbCount: number; rmpRating: number | null } | null }): { average: number; bbCount: number; rmpRating: number | null } | null {
    const bbRatings = group.bbRatings;
    const rmpRating = group.rmpRating;
    
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

  // Calculate combined rating for an instructor (average of RMP and Billiken Blueprint ratings)
  getCombinedRating(instructorId: number | null): { average: number; bbCount: number; rmpRating: number | null } | null {
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

  // Helper methods for template calculations
  getDisplayRating(group: { instructor: Instructor | null; rmpRating: Rating | null; bbRatings: Rating[]; combined: { average: number; bbCount: number; rmpRating: number | null } | null }): number {
    if (group.combined) {
      return group.combined.average;
    }
    if (group.rmpRating) {
      return group.rmpRating.rating;
    }
    if (group.bbRatings.length > 0) {
      return this.getBbAverage(group.bbRatings);
    }
    return 0;
  }

  getBbAverage(bbRatings: Rating[]): number {
    if (bbRatings.length === 0) return 0;
    const sum = bbRatings.reduce((acc, r) => acc + r.rating, 0);
    return sum / bbRatings.length;
  }
}
