export interface SimpleCourse {
    code: string;
    title: string;
}

export type GroupKey =
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
export const COURSE_GROUP_DATA: Record<GroupKey, SimpleCourse[]> = {
    // ---- Core Courses ----
    Core_Intro: [
        { code: 'CSCI 1010', title: 'Intro to Computer Science: Principles' },
        { code: 'CSCI 1020', title: 'Intro to Computer Science: Bioinformatics' },
        { code: 'CSCI 1025', title: 'Intro to Computer Science: Cybersecurity' },
        { code: 'CSCI 1030', title: 'Intro to Computer Science: Game Design' },
        { code: 'CSCI 1040', title: 'Intro to Computer Science: Mobile Computing' },
        { code: 'CSCI 1050', title: 'Intro to Computer Science: Multimedia' },
        { code: 'CSCI 1060', title: 'Intro to Computer Science: Scientific Programming' },
        { code: 'CSCI 1070', title: 'Intro to Computer Science: Taming Big Data' },
        { code: 'CSCI 1080', title: 'Intro to Computer Science: World Wide Web' },
        { code: 'CSCI 1090', title: 'Intro to Computer Science: Special Topics' }
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
        { code: 'MATH 2530', title: 'Calculus III' },
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
