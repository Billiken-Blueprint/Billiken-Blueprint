import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

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

@Component({
  selector: 'app-courses-page',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './courses-page.html',
  styleUrl: './courses-page.css',
  host: {
    class: 'block w-full h-full',
  },
})
export class CoursesPage {
  // === courses-page toolbox + groups state ===
  toolboxOpen = false;
  savedOpen = true;

  selectedGroup: GroupKey | null = null;
  expandedCourseCode: string | null = null;

  savedCourses: SimpleCourse[] = [];

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

  isCourseSaved(course: SimpleCourse): boolean {
    return this.savedCourses.some(c => c.code === course.code);
  }

  addCourse(course: SimpleCourse, event?: MouseEvent): void {
    event?.stopPropagation();
    if (!this.isCourseSaved(course)) {
      this.savedCourses.push(course);
    }
  }

  clearSaved(): void {
    this.savedCourses = [];
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
    }
  ]);

  toggleDesc(i: number) {
    const copy = [...this.courses()];
    copy[i] = { ...copy[i], expandedDesc: !copy[i].expandedDesc };
    this.courses.set(copy);
  }

  toggleInstructors(i: number) {
    const copy = [...this.courses()];
    copy[i] = { ...copy[i], expandedInstructors: !copy[i].expandedInstructors };
    this.courses.set(copy);
  }
}
