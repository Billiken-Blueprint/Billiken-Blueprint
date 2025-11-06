import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

type Instructor = {
  name: string;
  email?: string;
  office?: string;
  rating?: {
    overall: number;
    numRatings: number;
    rmpUrl?: string;
  };
};

type Course = {
  code: string;
  title: string;
  credits: number;
  meetingTimes?: string;
  location?: string;
  description?: string;
  prerequisites?: string;
  attributes?: string;

  instructors?: Instructor[];     // now supports multiple instructors

  // UI state
  expandedDesc?: boolean;
  expandedInstructors?: boolean;
};

@Component({
  selector: 'app-course-info',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './course-info.html',
  styleUrl: './course-info.css',
  host: { 'class': 'block min-h-screen w-full' }
})
export class CourseInfoPage {
  courses = signal<Course[]>([
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
      expandedDesc: false, expandedInstructors: false },
    { code: 'CSCI 2510', 
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
      expandedDesc: false, expandedInstructors: false }
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
