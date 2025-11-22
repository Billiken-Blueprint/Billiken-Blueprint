import { Component, ViewEncapsulation, signal, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { UserInfoService } from '../user-info-service/user-info-service';

interface SimpleCourse {
  code: string;
  title: string;
}

interface Rating {
  overall: number;
  numRatings: number;
  rmpUrl?: string;
}

interface Instructor {
  name: string;
  email?: string;
  office?: string;
  rating?: Rating;
}

interface InfoCourse {
  code: string;
  title: string;
  credits: number;
  meetingTimes?: string;
  location?: string;
  description?: string;
  prerequisites?: string;
  attributes?: string;
  instructors?: Instructor[];
  expandedDesc?: boolean;
  expandedInstructors?: boolean;
}

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

// This is adapted directly from your courses-page.js COURSE_DATA :contentReference[oaicite:2]{index=2}
const COURSE_GROUP_DATA: Record<GroupKey, SimpleCourse[]> = {
  // ---- Core Courses ----
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

  // ---- STEM & Ethics ----
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

  // ---- Electives ----
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

@Component({
  selector: 'app-course-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './course-page.html',
  styleUrls: ['./course-page.css'],
  encapsulation: ViewEncapsulation.None, // let body/html styles apply globally
  host: { 'class': 'block min-h-screen w-full' }
})
export class CoursePage implements OnInit {
  // === courses-page toolbox + groups state ===
  toolboxOpen = false;
  savedOpen = true;

  selectedGroup: GroupKey | null = null;
  expandedCourseCode: string | null = null;

  savedCourses: SimpleCourse[] = [];
  private userInfoService = inject(UserInfoService);

  readonly courseGroups: { key: GroupKey; label: string }[] = [
    { key: 'Core_Intro', label: 'Intro to CS' },
    { key: 'Core_Prog', label: 'Programming & Data Structures' },
    { key: 'Core_Software', label: 'Software Design & Engineering' },
    { key: 'Core_Systems', label: 'Systems & Architecture' },
    { key: 'Stem_MathCore', label: 'Math Core' },
    { key: 'Stem_MathAdv', label: 'Advanced Math & Stats' },
    { key: 'Stem_Science', label: 'Science & Engineering' },
    { key: 'Stem_Ethics', label: 'Ethics' },
    { key: 'Electives_Systems', label: 'Systems Electives' },
    { key: 'Electives_AIData', label: 'AI & Data Science' },
    { key: 'Electives_Software', label: 'Software & UX' },
    { key: 'Electives_Capstone', label: 'Capstone & Experience' }
  ];

  get groupCourses(): SimpleCourse[] {
    return this.selectedGroup ? COURSE_GROUP_DATA[this.selectedGroup] ?? [] : [];
  }

  onSelectGroup(key: GroupKey): void {
    this.selectedGroup = key;
    this.expandedCourseCode = null;
  }

  toggleCourseDescription(code: string): void {
    this.expandedCourseCode = this.expandedCourseCode === code ? null : code;
  }

  getCourseDetails(code: string): InfoCourse | undefined {
    return this.courses().find(c => c.code === code);
  }

  ngOnInit(): void {
    this.loadSavedCourses();
  }

  loadSavedCourses(): void {
    this.userInfoService.getUserInfo().subscribe({
      next: (userInfo) => {
        if (userInfo.savedCourseCodes && userInfo.savedCourseCodes.length > 0) {
          // Map saved course codes to SimpleCourse objects
          this.savedCourses = userInfo.savedCourseCodes
            .map(code => {
              // Find the course in all groups
              for (const group of Object.values(COURSE_GROUP_DATA)) {
                const course = group.find(c => c.code === code);
                if (course) return course;
              }
              // If not found in groups, create a simple entry
              return { code, title: code };
            })
            .filter(c => c !== null) as SimpleCourse[];
        }
      },
      error: (error) => {
        console.error('Error loading saved courses:', error);
        // If user is not logged in or no profile exists, that's okay
        // Saved courses will just be empty
      }
    });
  }

  isCourseSaved(course: SimpleCourse): boolean {
    return this.savedCourses.some(c => c.code === course.code);
  }

  addCourse(course: SimpleCourse, event?: MouseEvent): void {
    event?.stopPropagation();
    if (!this.isCourseSaved(course)) {
      this.savedCourses.push(course);
      this.saveCoursesToBackend();
    }
  }

  removeCourse(course: SimpleCourse): void {
    this.savedCourses = this.savedCourses.filter(c => c.code !== course.code);
    this.saveCoursesToBackend();
  }

  clearSaved(): void {
    this.savedCourses = [];
    this.saveCoursesToBackend();
  }

  private saveCoursesToBackend(): void {
    const savedCourseCodes = this.savedCourses.map(c => c.code);
    this.userInfoService.updateSavedCourses(savedCourseCodes).subscribe({
      next: () => {
        // Successfully saved
      },
      error: (error) => {
        console.error('Error saving courses:', error);
        // Don't show error to user - courses are still in memory
        // They'll be lost on refresh, but that's acceptable for now
      }
    });
  }

  // === course-info state (merged from course-info.ts) ===
  courses = signal<InfoCourse[]>([
    {
      code: 'CSCI 1300',
      title: 'Introduction to Object-Oriented Programming',
      credits: 4,
      description:
        'A rigorous introduction to programming using an object-oriented language, including variables, control structures, recursion, user-defined functions/classes, and good software development practices.',
      prerequisites:
        '((0 Course from CSCI 1010-1090 with C- or higher, BME 2000 with C- or higher, CVNG 1500 with C- or higher, MATH 3850 with C- or higher, STAT 3850 with C- or higher, ECE 1001 with C- or higher, or GIS 4090 with C- or higher); (MATH 1200 or 0 Course from MATH 1320-4999))',
      attributes: 'Foreign Language BA Req (CAS)',
      meetingTimes: 'MTWTh 10:00–10:50 | MTWF 11:00-11:50',
      location: 'Ritter 231 | BSC 253',
      instructors: [
        {
          name: 'David Letscher',
          email: 'david.letscher@slu.edu',
          office: 'Ritter 359',
          rating: { overall: 2.7, numRatings: 52, rmpUrl: 'https://www.ratemyprofessors.com/professor/325024' }
        },
        {
          name: 'Michael Liljegren',
          email: 'mike.liljegren@slu.edu',
          office: 'Ritter',
          rating: { overall: 4.4, numRatings: 7, rmpUrl: 'https://www.ratemyprofessors.com/professor/2999302' }
        },
      ],
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 2100',
      title: 'Data Structures',
      credits: 4,
      description:
        'The design, implementation and use of data structures. Principles of abstraction, encapsulation and modularity to guide in the creation of robust, adaptable, reusable and efficient structures. Specific data types to include stacks, queues, dictionaries, trees and graphs.',
      prerequisites:
        '(CSCI 1300 with a grade of C- or higher and MATH 1660*)* Concurrent enrollment allowed.',
      meetingTimes: 'MTWTh 10:00–10:50',
      location: 'SSEC 230',
      instructors: [
        {
          name: 'Michael Goldwasser',
          email: 'michael.goldwasser@slu.edu',
          office: 'Ritter 217',
          rating: { overall: 4.2, numRatings: 24, rmpUrl: 'https://www.ratemyprofessors.com/professor/278739' }
        }
      ],
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 2300',
      title: 'Object-Oriented Software Design',
      credits: 3,
      description:
        'An implementation-based study of object-oriented software development. Teams will design and create medium-scale applications. Additional focus on the design and use of large object-oriented libraries, as well as social and professional issues.',
      prerequisites:
        'CSCI 2100 with a grade of C- or higher',
      meetingTimes: 'MWF 1:10–2:00 | MWF 2:10–3:00',
      location: 'SSEC 230',
      instructors: [
        {
          name: 'John Allen',
          email: 'NA',
          office: 'NA'
        }
      ],
      expandedDesc: false,
      expandedInstructors: false
    },
    { 
      code: 'CSCI 2500',
      title: 'Computer Organization and Systems', 
      credits: 3, 
      description:
        'An introduction to computer systems, from hardware to operating systems. Topics include computer architecture, instruction sets, data representation, memory systems, and how the operating system manages processes and user applications. (Offered in Fall)',
      prerequisites:
        '(CSCI 2100)* Concurrent enrollment allowed.',
      meetingTimes: 'MWF 2:10–3:00',
      location: 'Ritter 115',
      expandedDesc: false, 
      expandedInstructors: false 
    },
    {
      code: 'CSCI 2510',
      title: 'Principles of Computing Systems',
      credits: 3,
      description:
        'An exploration of computing systems with a strong emphasis on how systems interact with each other. Topics will include concurrent and parallel programming, network communication, and computer security. In addition to foundational knowledge, the course includes simulating, benchmarking, and testing such systems.',
      prerequisites:
        '(CSCI 2500 with a grade of C- or higher or (ECE 2205, ECE 3217, and ECE 3225))',
      meetingTimes: 'TTh 12:45-2:00',
      location: 'BSC 253',
      instructors: [
        {
          name: 'Qinglei Cao',
          email: 'qinglei.cao@slu.edu',
          office: 'Ritter',
          rating: { overall: 2.9, numRatings: 7, rmpUrl: 'https://www.ratemyprofessors.com/professor/3010174' }
        }
      ],
      expandedDesc: false, 
      expandedInstructors: false 
    },
    { 
      code: 'CSCI 3100', 
      title: 'Algorithms', 
      credits: 3,
      description: 'Introduction to analysis and complexity of algorithms. Big-O notation. Running time analysis of algorithms for traversing graphs and trees, searching and sorting. Recursive versus iterative algorithms. Complexity, completeness, computability.',
      prerequisites:
        'CSCI 2100; MATH 1660; (MATH 1510, MATH 1520, MATH 2530, and SLU Math Placement with a minimum score of 1520)',
      meetingTimes: 'TTh 11-12:15',
      location: 'SSEC 230',
      instructors: [
        {
          name: 'Michael Goldwasser',
          email: 'michael.goldwasser@slu.edu',
          office: 'Ritter 217',
          rating: { overall: 4.2, numRatings: 24, rmpUrl: 'https://www.ratemyprofessors.com/professor/278739' }
        }
      ],
      expandedDesc: false, 
      expandedInstructors: false 
    },
    { 
      code: 'CSCI 3200', 
      title: 'Programming Languages', 
      credits: 3,
      description: 'Overview of programming languages: procedural and functional languages. Exposure to functional languages. Analysis of solution strategies to variable binding and function calls. Problem solving paradigms and linguistic issues.',
      prerequisites:'CSCI 2300',
      meetingTimes: 'TTh 12:45-2:00',
      location: 'MDD 2096',
      instructors: [
        {
          name: 'David Letscher',
          email: 'david.letscher@slu.edu',
          office: 'Ritter 359',
          rating: { overall: 2.7, numRatings: 52, rmpUrl: 'https://www.ratemyprofessors.com/professor/325024' }
        },
      ],
      expandedDesc: false, 
      expandedInstructors: false 
    },
    { 
      code: 'CSCI 3300', 
      title: 'Software Engineering', 
      credits: 3, 
      description: 'Theory and practice of software engineering. Design and implementation of software systems. Levels of abstraction as a technique in program design. Organized around major group programming projects.',
      prerequisites: 'CSCI 2300',
      meetingTimes: 'TTh 3:45-5:00',
      location: 'Ritter 346',
      instructors: [
        {
          name: 'Ankit Agrawal',
          email: 'ankit.agrawal.1@slu.edu',
          office: 'MDD 2010',
        },
      ],
      expandedDesc: false, 
      expandedInstructors: false 
    },
    { 
      code: 'CSCI 4961', 
      title: 'Capstone Project I', 
      credits: 2, 
      description: 'The first part of a two-course sequence serving as a concluding achievement for graduating students. In this course, students develop a proposal, collect and formalize specifications, become acquainted with necessary technologies, and create and present a detailed design for completing the project.',
      prerequisites: 'CSCI 2300; (CSCI 2510 or ECE 3127)',
      meetingTimes: 'M 4:10-5:40',
      location: 'BSC 253',
      instructors: [
        {
          name: 'Daniel Shown',
          email: 'NA',
          office: 'NA',
        }
      ],
      expandedDesc: false,
      expandedInstructors: false 
    },
    { 
      code: 'CSCI 4962', 
      title: 'Capstone Project II', 
      credits: 2, 
      description: 'The continuation of CSCI 4961. In the second part of the sequence, students complete their project based upon the design that was developed during the first part of the sequence. Students must demonstrate continued progress throughout the semester and make a preliminary and final presentation of their results.',
      prerequisites: 'CSCI 4961',
      meetingTimes: 'M 4:10-5:40',
      location: 'BSC 253',
      instructors: [
        {
          name: 'Daniel Shown',
          email: 'NA',
          office: 'NA',
        }
      ],     
      expandedDesc: false, 
      expandedInstructors: false 
    },
    // Capstone & Experience courses
    {
      code: 'CSCI 1930',
      title: 'Special Topics (Lower Division)',
      credits: 4,
      description: 'Special topics offerings at the lower division level. Content varies by semester. 1-4 Credits (Repeatable for credit).',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 1980',
      title: 'Independent Study (Lower Division)',
      credits: 3,
      description: 'Independent study at the lower division level. Students work under the supervision of a faculty member on a topic of mutual interest. 1-3 Credits (Repeatable for credit).',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 2930',
      title: 'Special Topics (Middle Division)',
      credits: 4,
      description: 'Special topics offerings at the middle division level. Content varies by semester. 1-4 Credits (Repeatable for credit).',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 2980',
      title: 'Independent Study (Middle Division)',
      credits: 3,
      description: 'Independent study at the middle division level. Students work under the supervision of a faculty member on a topic of mutual interest. Prior approval of sponsoring professor and chair required. 1-3 Credits (Repeatable for credit).',
      prerequisites: undefined,
      attributes: 'Special Approval Required',
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 3910',
      title: 'Internship with Industry',
      credits: 6,
      description: 'A work experience with an agency, firm, or organization that employs persons in this degree field. Learning plan and follow-up evaluation required. 1-6 Credits (Repeatable for credit).',
      prerequisites: '(CORE 1000 or UUC Ignite Seminar Waiver with a minimum score of S); CORE 1500* Concurrent enrollment allowed.',
      attributes: 'UUC:Reflection-in-Action',
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 3930',
      title: 'Special Topics (Upper Division)',
      credits: 4,
      description: 'Special topics offerings at the upper division level. Content varies by semester. 1-4 Credits (Repeatable for credit).',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 3980',
      title: 'Independent Study (Upper Division)',
      credits: 3,
      description: 'Independent study at the upper division level. Students work under the supervision of a faculty member on a topic of mutual interest. Prior approval of sponsoring professor and chairperson required. 1-3 Credits (Repeatable for credit).',
      prerequisites: undefined,
      attributes: 'Special Approval Required',
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 4910',
      title: 'Internship with Industry (Advanced)',
      credits: 6,
      description: 'An advanced work experience with an agency, firm, or organization that employs persons in this degree field. Learning plan and follow-up evaluation required. 1-6 Credits (Repeatable for credit).',
      prerequisites: '(CORE 1000 or UUC Ignite Seminar Waiver with a minimum score of S); CORE 1500* Concurrent enrollment allowed.',
      attributes: 'UUC:Reflection-in-Action',
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 4930',
      title: 'Special Topics',
      credits: 4,
      description: 'Special topics offerings at the upper division level. Content varies by semester. 1-4 Credits (Repeatable for credit).',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 4980',
      title: 'Advanced Independent Study',
      credits: 6,
      description: 'Advanced independent study. Students work under the supervision of a faculty member on an advanced topic of mutual interest. Prior permission of sponsoring professor and chairperson required. 1-3 Credits (Repeatable up to 9 credits).',
      prerequisites: undefined,
      attributes: 'Special Approval Required',
      expandedDesc: false,
      expandedInstructors: false
    },
    // Ethics courses
    {
      code: 'PHIL 2050',
      title: 'Ethics',
      credits: 3,
      description: 'An introduction to the philosophical study of morality, this course tackles questions like "What is a good human life?" "What makes an action right?" and "What makes a social practice just?" We explore major ethical theories including deontological ethics, consequentialist ethics, and virtue ethics, considering the potential strengths and weaknesses of each theory. We also consider how these theories direct us to behave in real-life situations. By applying ethical theories to living questions, students learn to evaluate both the morality of their individual actions and the justice of the systems and practices that structure our society.',
      prerequisites: undefined,
      attributes: 'Catholic Studies-Philosophy, Health Care Ethics Minor Elec, IPE - Ethics, Philosophy Requirement (A&S), UUC:Dignity, Ethics & Just Soc',
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'PHIL 3000',
      title: 'Advanced Ethics & Technology',
      credits: 3,
      description: 'An advanced examination of ethical issues related to technology, including artificial intelligence, data privacy, algorithmic bias, and the social impact of technological innovation. Students will apply advanced ethical theories to contemporary technological challenges.',
      prerequisites: 'PHIL 2050',
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'PHIL 3050X',
      title: 'Computer Ethics',
      credits: 3,
      description: 'This course examines the moral, legal, and social issues raised by computers and electronic information technologies for different stakeholder groups (professionals, users, businesses, etc.). Students are expected to integrate moral theories and social analysis to address such issues as intellectual property, security, privacy, discrimination, globalization, and community.',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 3050',
      title: 'Computer Ethics (CSCI listing)',
      credits: 3,
      description: 'This course examines the moral, legal, and social issues raised by computers and electronic information technologies for different stakeholder groups (professionals, users, businesses, etc.). Students are expected to integrate moral theories and social analysis to address such issues as intellectual property, security, privacy, discrimination, globalization, and community.',
      prerequisites: 'PHIL 2050',
      attributes: 'Philosophy Requirement (A&S), UUC:Dignity, Ethics & Just Soc',
      expandedDesc: false,
      expandedInstructors: false
    },
    // Additional CSCI courses from PDFs
    {
      code: 'CSCI 1010',
      title: 'Introduction to Computer Science: Principles',
      credits: 3,
      description: 'A broad survey of the computer science discipline, focusing on the computer\'s role in representing, storing, manipulating, organizing and communicating information. Topics include hardware, software, algorithms, operating systems, networks.',
      prerequisites: undefined,
      attributes: 'CSCI Intro to Computer Science',
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 1020',
      title: 'Introduction to Computer Science: Bioinformatics',
      credits: 3,
      description: 'An introduction to computer programming motivated by the analysis of biological data sets and the modeling of biological systems. Computing concepts to include data representation, control structures, text processing, input and output. Applications to include the representation and analysis of protein and genetic sequences, and the use of available biological data sets.',
      prerequisites: undefined,
      attributes: 'Bio-Chemical Biology Elective, Chemical Biology Elective, CSCI Intro to Computer Science, UUC:Natural & Applied Science',
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 1025',
      title: 'Introduction to Computer Science: Cybersecurity',
      credits: 3,
      description: 'An introduction to the fundamental principles of computer and network security, privacy-preserving communication techniques, and an overview of prominent attacks on computer systems, networks, and the Web. Students will gain an understanding of security and privacy, including vulnerabilities and requirements of a secure system, and will conduct a series of lab exercises to explore these topics.',
      prerequisites: undefined,
      attributes: 'CSCI Intro to Computer Science',
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 1030',
      title: 'Introduction to Computer Science: Game Design',
      credits: 3,
      description: 'Introduces the design of computer and video games. Students learn the practical aspects of game implementation using computer game engines and 3D graphics tools, while simultaneously studying game concepts like history, genres, storylines, gameplay elements and challenges, and the design process.',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 1040',
      title: 'Introduction to Computer Science: Mobile Computing',
      credits: 3,
      description: 'An introduction to programming based on the development of apps for mobile devices such as phones and tablets. Students will learn to design an effective user interface, to interact with device hardware and sensors, to store data locally and access Internet resources.',
      prerequisites: undefined,
      attributes: 'CSCI Intro to Computer Science',
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 1050',
      title: 'Introduction to Computer Science: Multimedia',
      credits: 3,
      description: 'An introduction to computer programming, motivated by the creation and manipulation of images, animations, and audio. Traditional software development concepts, such as data representation and control flow, are introduced for the purpose of image processing, data visualization, and the synthesis and editing of audio.',
      prerequisites: undefined,
      attributes: 'CSCI Intro to Computer Science, UUC:Creative Expression',
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 1060',
      title: 'Introduction to Computer Science: Scientific Programming',
      credits: 3,
      description: 'Elementary computer programming concepts with an emphasis on problem solving and applications to scientific and engineering applications. Topics include data acquisition and analysis, simulation and scientific visualization.',
      prerequisites: '(MATH 1510 or SLU Math Placement with a minimum score of 1520) * Concurrent enrollment allowed.',
      attributes: 'CSCI Intro to Computer Science, Foreign Language BA Req (CAS), UUC:Quantitative Reasoning',
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 1070',
      title: 'Introduction to Computer Science: Taming Big Data',
      credits: 3,
      description: 'An introduction to data science and machine learning. Fundamentals of data representation and analysis will be covered, with a focus on real-world applications to business intelligence, natural language processing, and social network analysis.',
      prerequisites: undefined,
      attributes: 'CSCI Intro to Computer Science, UUC:Quantitative Reasoning',
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 1080',
      title: 'Introduction to Computer Science: World Wide Web',
      credits: 3,
      description: 'An introduction to the technology of the web, from the structure of the Internet (web science) to the design of dynamic web pages (web development). The web science component of the class introduces notions of the web as an example of a network and use the tools of graph theory to better understand the web. The web development component introduces some of the fundamental languages and tools for web programming.',
      prerequisites: undefined,
      attributes: 'CSCI Intro to Computer Science',
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 1090',
      title: 'Introduction to Computer Science: Special Topics',
      credits: 3,
      description: '(Repeatable for credit) Special topics offerings that qualify for CSCI 10XX: Introduction to Computer Science credit.',
      prerequisites: undefined,
      attributes: 'CSCI Intro to Computer Science',
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 2190',
      title: 'Computational Problem Solving',
      credits: 1,
      description: 'Intended primarily to train students for the International Collegiate Programming Contest (ICPC), this course covers data structures, algorithms, and programming techniques that apply to typical programming challenges.',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 3250',
      title: 'Compilers',
      credits: 3,
      description: 'Introduction to the theory and techniques of compiler design, lexical analysis, finite state automata, context-free grammars, top-down and bottom-up parsing, syntax analysis, code generation. Other important issues such as optimization, type-checking, and garbage collection will be discussed.',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 3450X',
      title: 'Microprocessors',
      credits: 3,
      description: 'Review of number systems. Microprocessors/microcomputer structure, input/output. Signals and devices. Computer arithmetic, programming, interfacing and data acquisition. Fall semester.',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 3451X',
      title: 'Microprocessors Laboratory',
      credits: 1,
      description: 'Concurrent registration with ECE 3225. Laboratory experiments to emphasize materials covered in ECE 3225. Corequisite(s): ECE 3225',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 3710',
      title: 'Databases',
      credits: 3,
      description: 'Fundamentals of database systems. Topics include relational and NoSQL data models, structured query language, the entity-relationship model, normalization, transactions, file organization and indexes, and data security issues. The knowledge of the listed topics is applied to design and implementation of a database application.',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 3810',
      title: 'Game Programming',
      credits: 3,
      description: 'Introduction to the programming and development of computer/video games, especially through the use of a computer game engine (e.g. Unity, Unreal, etc.). Course will cover the major aspects of programming and creating games within a game engine, including world/level design, programming within a game engine, basic interaction between code and game assets (character, buildings, objects, weapons, camera, etc.), movement and manipulation of game assets, events such as object collisions, triggers, and timed events, common gameplay mechanics, creating a game interface (HUD), non-player characters and AI, and animation and game sequences. The course is a project-based course, culminating with the students integrating the many topics and tools to develop their own complete game.',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 4120',
      title: 'Advanced Data Structures',
      credits: 3,
      description: 'A comprehensive treatment of the design, analysis and implementation of advanced data structures, and their role in algorithmic design. Topics include data structures that are dynamic, persistent and/or cache-oblivious, an examination of performance including both amortized and probabilistic analyses, and domain-specific applications of data structures. (Offered occasionally)',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 4310',
      title: 'Software Architecture',
      credits: 3,
      description: 'The theory and practice of software architecture and global design of software systems, with focus on recurring architectural patterns via in-depth case studies of various large-scale systems. (Offered occasionally)',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 4340',
      title: 'Safety-Critical Software Systems',
      credits: 3,
      description: 'This course provides an introduction to current processes guiding the development of software for safety-critical systems. The primary standard used is RTCA\'s DO-178C used by FAA for aviation, with additional discussion of the standards used by military and space programs. The general approach is also applicable to medical devices and emerging automotive safety standards.',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 4355',
      title: 'Human Computer Interaction',
      credits: 3,
      description: 'You will engage in an in-depth exploration of the field of Human-Computer Interaction (HCI) including its history, goals, principles, methodologies, successes, failures, open problems, and emerging areas. Broad topics include theories of interaction (e.g., conceptual models, stages of execution, error analysis, constraints, memory by affordances), design methods (e.g., user-centered design, task analysis, prototyping tools), visual design principles (e.g., visual communication, digital typography, color, motion), evaluation techniques (e.g., heuristic evaluations, model-based evaluations), and emerging topics (e.g., information visualization, affective computing, natural user interfaces).',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 4360',
      title: 'Web Technologies',
      credits: 3,
      description: 'An overview of the client-side and server-side technologies that power the modern web. Hands-on experience with interactive web site and web application development for desktop and mobile. (Offered occasionally)',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 4370',
      title: 'User Interface Design',
      credits: 3,
      description: 'Examination of the theory, design, programming, and evaluation of interactive application interfaces. Topics include human capabilities and limitations, the interface design and engineering process, prototyping and interface construction, interface evaluation.',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 4380',
      title: 'DevOps',
      credits: 3,
      description: 'Software engineering practices require knowledge of the environment in which an application is to be run. In the modern world, this means knowledge of virtualization, containers, networking, the cloud, and security techniques for the internet. A developer should also know about microservices, configuration management, the deployment pipeline, monitoring and post-production, disaster recovery, and how to develop secure applications.',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 4500',
      title: 'Operating Systems',
      credits: 3,
      description: 'This comprehensive course delves into the fundamental theories and practical applications of operating systems as effective managers of shared computer hardware resources such as processors, memory, mass storage devices, and peripheral components. Additionally, it introduces students to the essential principles of computer networking. Through hands-on experiences, students will gain expertise in general systems programming, concurrent and parallel programming techniques, and network programming.',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 4520',
      title: 'Internet of Things',
      credits: 3,
      description: 'The course introduces the concepts and principles of Internet of Things development and management. It covers an overview of the IoT device hardware and software modules, along with their communication capabilities over Internet. The ultimate goal is to be able to understand the common issues of IoT development, from the design phase, to the choice of sensors and actuators, the communication model, and the software development. From the practical point of view, the course provides hands-on experience with real and simulated devices.',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 4530',
      title: 'Computer Security',
      credits: 3,
      description: 'Fundamental introduction to the broad area of computer security. Topics include access control, security policy design, network security, cryptography, ethics, securing systems, and common vulnerabilities in computer systems.',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 4550',
      title: 'Computer Networks',
      credits: 3,
      description: 'An exploration of the underlying concepts and principles of computer networks. Topics include communication protocols such as TCP/IP, design of network architectures, and the management and security of networks. Examples of real networks will be used to reinforce and demonstrate concepts.',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 4590',
      title: 'Wireless Sensor Networks',
      credits: 3,
      description: 'The goal of this course is to let students have a deep understanding of Wireless Sensor Networks (WSN). We will cover multiple important topics in WSN, including WSN Applications and Design Model, Network models, Network Bootstrapping, Data Dissemination and Routing, Link Layers Design, and Dependability Issues, etc. Students are also required to read multiple papers and present papers in the class. In the paper reading section, a group of students should present a paper and find technical drawbacks of the paper. The presenters should also answer the questions from the audience.',
      prerequisites: 'MATH 3110',
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 4610',
      title: 'Concurrent and Parallel Programming',
      credits: 3,
      description: 'The design and implementation of software that fully leverages a single computer\'s resources. Topics include profiling and optimization of codes, multi-threaded programming, parallelism using a graphical processor unit (GPU), and efficient use of memory cache. (Offered occasionally)',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 4620',
      title: 'Distributed Computing',
      credits: 3,
      description: 'The design and implementation of software solutions that rely upon the cooperation of multiple computing systems. Topics will include parallelization of computation and data storage across small clusters of computers, and the deployment of systems in large-scale grid and cloud computing environments. (Offered occasionally)',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 4710',
      title: 'Databases',
      credits: 3,
      description: 'Fundamentals of database systems. Topics include relational and NoSQL data models, structured query language, the entity-relationship model, normalization, transactions, file organization and indexes, and data security issues. The knowledge of the listed topics is applied to design and implementation of a database application.',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 4740',
      title: 'Artificial Intelligence',
      credits: 3,
      description: 'Fundamental introduction to the broad area of artificial intelligence and its applications. Topics include knowledge representation, logic, search spaces, reasoning with uncertainty, and machine learning.',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 4750',
      title: 'Machine Learning',
      credits: 3,
      description: 'This course introduces students to the field of machine learning with emphasis on the probabilistic models that dominate contemporary applications. Students will discover how computers can learn from examples and extract salient patterns hidden in large data sets. The course will introduce classification algorithms that predict discrete states for variables as well as regression algorithms that predict continuous values for variables. Attention will be given to both supervised and unsupervised settings in which (respectively) labeled training data is or is not available.',
      prerequisites: 'STAT 3850',
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 4756',
      title: 'Applied Machine Learning',
      credits: 3,
      description: 'The course introduces the concepts, algorithms, and applications for modern machine learning approaches. Students will learn the theoretical foundations of supervised learning methods in which labeled training data is available for regression/classification problems. Attention will also be given to unsupervised learning when the label information of the training data is missing. Topics include linear regression, nonlinear regression, support vector machines, neural networks, deep learning, ensemble methods, probabilistic models, clustering, and dimensionality reduction. Emphasis is placed on the mathematical formulation of the machine learning models and their practical applications on various research questions.',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 4760',
      title: 'Deep Learning',
      credits: 3,
      description: 'An exploration of multi-layered machine learning architectures as applied to problems in a variety of domains. The course will study various network architectures including deep feed-forward, convolutional and recurrent networks, and uses in both supervised and unsupervised learning. Students will implement solutions in different problem domains, and learn to effectively manage practical and domain-specific issues that affect model performance. (Offered in Spring)',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 4770',
      title: 'Big Data Analytics',
      credits: 3,
      description: 'This course will introduce basic concepts in the business analytics field, along with some popular techniques and tools. Students will have opportunities to explore and analyze large quantities of observational data in order to discover meaningful patterns and useful information to support decision making in business contexts.',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 4780',
      title: 'Data Engineering',
      credits: 3,
      description: 'This course introduces students to the objectives and techniques of data engineering as a critical step in the effective application of machine learning and other data analysis techniques. The course will include data selection and profiling to improve the nature and understanding of the problem space; transformation and aggregation to cleanse and consolidate data; and feature engineering to expose critical characteristics for downstream analytics. Through instructor-provided programming assignments and self-designed projects, by the end of this course students will be able to implement data processing pipelines that transform data from their raw format into datasets useful for analysis.',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 4820',
      title: 'Computer Graphics',
      credits: 3,
      description: 'Applications and implementation of computer graphics. Algorithms and mathematics for creating two and three dimensional figures. Animation and two and three dimensional transformations. Interaction, windowing, and perspective techniques. Coding using the graphics library OpenGL.',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 4830',
      title: 'Computer Vision',
      credits: 3,
      description: 'This course will introduce the fundamentals of image processing and computer vision, including image models and representation, image analysis methods such as feature extraction (color, texture, edges, shape, skeletons, etc.), image transformations, image segmentation, image understanding, motion and video analysis, and application-specific methods such as medical imaging, facial recognition, and content-based image retrieval. (Offered occasionally)',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 4845',
      title: 'Natural Language Processing',
      credits: 3,
      description: 'Introduction to the development of computer systems that attempt to manage the complexity and diversity of human language. Application of artificial intelligence and machine learning techniques to address problems such as machine translation and speech recognition. Emphasis to be placed on working with real data sets in the form of text corpora and sound recordings. (Offered occasionally)',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 4860',
      title: 'Autonomous Driving',
      credits: 3,
      description: 'The goal of this course is to introduce the basics of autonomous vehicle and automated driving system (ADS). We will introduce SAE levels, ADS architecture, Vehicle Models, Sensors and Sensor Fusion, Basics of SLAM, Vehicle Control Theory and Algorithms, and Famous ADS Solutions. Students are also required to read multiple papers and present the papers in the class. In the paper reading section, a group of students should present a paper and find the technical drawbacks of the paper. The presenters should also answer the questions from the audience.',
      prerequisites: 'MATH 3110',
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'CSCI 4870',
      title: 'Applied Cryptography',
      credits: 3,
      description: 'An overview of the topic of cryptography from a computer science perspective, including the study of basic cryptographic algorithms and the mathematics behind them. Students will also be able to understand security system design and apply the basics to more complex systems using common programming libraries and tools.',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    // MATH courses from PDFs
    {
      code: 'MATH 1510',
      title: 'Calculus I',
      credits: 4,
      description: 'Functions; continuity; limits; the derivative; differentiation from graphical, numerical and analytical viewpoints; optimization and modeling; rates and related rates; the definite integral; antiderivatives from graphical, numerical and analytical viewpoints.',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'MATH 1520',
      title: 'Calculus II',
      credits: 4,
      description: 'Symbolic and numerical techniques of integration, improper integrals, applications using the definite integral, sequences and series, power series, Taylor series, differential equations. (Offered every Fall, Spring and Summer)',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'MATH 1660',
      title: 'Discrete Mathematics',
      credits: 3,
      description: 'Concepts of discrete mathematics used in computer science; sets, sequences, strings, symbolic logic, proofs, mathematical induction, sums and products, number systems, algorithms, complexity, graph theory, finite state machines.',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'MATH 2530',
      title: 'Calculus III',
      credits: 4,
      description: 'Three-dimensional analytic geometry, vector-valued functions, partial differentiation, multiple integration, and line integrals. (Offered every Fall and Spring)',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'MATH 3110',
      title: 'Linear Algebra for Engineers',
      credits: 3,
      description: 'Systems of linear equations, matrices, linear programming, determinants, vector spaces, inner product spaces, eigenvalues and eigenvectors, linear transformations, and numerical methods.',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'MATH 3120',
      title: 'Introduction to Linear Algebra',
      credits: 3,
      description: 'Systems of linear equations, matrices, linear programming, determinants, vector spaces, inner product spaces, eigenvalues and eigenvectors, linear transformations, and numerical methods.',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'MATH 3730',
      title: 'Numerical Methods',
      credits: 3,
      description: 'Numerical methods for solving mathematical problems. Topics include numerical solutions to equations, interpolation, numerical differentiation and integration, and numerical solutions to differential equations.',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'MATH 4100',
      title: 'Advanced Topics in Math',
      credits: 3,
      description: 'Advanced topics in mathematics. Content varies by semester. (Repeatable for credit)',
      prerequisites: undefined,
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'STAT 3850',
      title: 'Foundation of Statistics',
      credits: 3,
      description: 'Introduction to statistical methods and their applications. Topics include descriptive statistics, probability, sampling distributions, estimation, hypothesis testing, and regression analysis.',
      prerequisites: 'MATH 1520',
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'STAT 4000',
      title: 'Advanced Statistics',
      credits: 3,
      description: 'Advanced statistical methods and their applications. Topics include advanced regression analysis, analysis of variance, nonparametric methods, and multivariate statistics.',
      prerequisites: 'STAT 3850',
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'STAT 4100',
      title: 'Applied Statistics',
      credits: 3,
      description: 'Application of statistical methods to real-world problems. Topics include experimental design, data analysis, and statistical modeling.',
      prerequisites: 'STAT 3850',
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    },
    {
      code: 'STAT 4200',
      title: 'Probability and Statistics',
      credits: 3,
      description: 'Probability theory and statistical inference. Topics include probability distributions, random variables, sampling theory, estimation, and hypothesis testing.',
      prerequisites: 'MATH 2530',
      attributes: undefined,
      expandedDesc: false,
      expandedInstructors: false
    }
  ]);

  getCourseIndex(code: string): number {
    return this.courses().findIndex(c => c.code === code);
  }

  toggleDesc(code: string) {
    const index = this.getCourseIndex(code);
    if (index === -1) return;
    const copy = [...this.courses()];
    copy[index] = { ...copy[index], expandedDesc: !copy[index].expandedDesc };
    this.courses.set(copy);
  }

  toggleInstructors(code: string) {
    const index = this.getCourseIndex(code);
    if (index === -1) return;
    const copy = [...this.courses()];
    copy[index] = { ...copy[index], expandedInstructors: !copy[index].expandedInstructors };
    this.courses.set(copy);
  }
}
