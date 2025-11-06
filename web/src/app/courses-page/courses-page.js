document.addEventListener('DOMContentLoaded', () => {
  const buttons = document.querySelectorAll('.action-btn');
  const cardContainer = document.getElementById('course-cards');
  const initialMessage = document.getElementById('initial-message');

  const toolbox = document.getElementById('toolbox');
  const toggleButton = document.getElementById('toolbox-toggle');
  const menuIcon = document.getElementById('menu-icon');
  const closeIcon = document.getElementById('close-icon');

  const savedToggle = document.getElementById('saved-toggle');
  const savedToggleIcon = document.getElementById('saved-toggle-icon');
  const savedPanel = document.getElementById('saved-panel');
  const savedList = document.getElementById('saved-list');
  const clearSavedBtn = document.getElementById('clear-saved');

  // TOOLBOX TOGGLE 
  toggleButton?.addEventListener('click', () => {
    toolbox?.classList.toggle('open');
    const isOpen = toolbox?.classList.contains('open');
    if (isOpen) {
      menuIcon?.classList.add('hidden');
      closeIcon?.classList.remove('hidden');
    } else {
      menuIcon?.classList.remove('hidden');
      closeIcon?.classList.add('hidden');
    }
  });

  // SAVED COURSES
  const savedCourses = new Map(); 

  const renderSavedCourses = () => {
    savedList.innerHTML = '';

    if (savedCourses.size === 0) {
      const li = document.createElement('li');
      li.className = 'text-white/70';
      li.textContent = 'No courses saved yet.';
      savedList.appendChild(li);
      return;
    }

    savedCourses.forEach((course) => {
      const li = document.createElement('li');
      li.className = 'flex items-center justify-between gap-2 bg-white/10 rounded px-2 py-1';
      li.textContent = `${course.code} – ${course.title}`;
      savedList.appendChild(li);
    });
  };

  const markButtonsForSavedCourses = () => {
    const addButtons = document.querySelectorAll('.add-course-btn');
    addButtons.forEach((btn) => {
      const code = btn.getAttribute('data-code');
      if (code && savedCourses.has(code)) {
        setButtonAddedState(btn);
      } else {
        setButtonDefaultState(btn);
      }
    });
  };

  const setButtonAddedState = (btn) => {
    btn.textContent = '✔ Added';
    btn.disabled = false;
    btn.className =
      'add-course-btn absolute top-2 right-2 text-xs px-2 py-1 rounded-full bg-green-400 text-[#003DA5] font-semibold shadow';
  };

  const setButtonDefaultState = (btn) => {
    btn.textContent = '+ Add';
    btn.disabled = false;
    btn.className =
      'add-course-btn absolute top-2 right-2 text-xs px-2 py-1 rounded-full bg-[#53C3EE] text-[#003DA5] font-semibold shadow';
  };

  // Accordion  for "My Saved Courses"
  savedToggle?.addEventListener('click', () => {
    if (!savedPanel) return;
    const isHidden = savedPanel.classList.contains('hidden');
    savedPanel.classList.toggle('hidden', !isHidden);
    savedToggleIcon.textContent = isHidden ? '▾' : '▸';
  });

  // Clear all saved courses
  clearSavedBtn?.addEventListener('click', () => {
    savedCourses.clear();
    renderSavedCourses();
    markButtonsForSavedCourses();
  });

  const COURSE_DATA = {
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
      { code: 'CSCI 1090', title: 'Introduction to Computer Science: Special Topics' },
    ],
    Core_Prog: [
      { code: 'CSCI 1300', title: 'Introduction to Object-Oriented Programming' },
      { code: 'CSCI 2100', title: 'Data Structures' },
      { code: 'CSCI 2190', title: 'Computational Problem Solving' },
      { code: 'CSCI 2300', title: 'Object-Oriented Software Design' },
      { code: 'CSCI 3100', title: 'Algorithms' },
      { code: 'CSCI 3200', title: 'Programming Languages' },
      { code: 'CSCI 3250', title: 'Compilers' },
      { code: 'CSCI 3300', title: 'Software Engineering' },
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
      { code: 'CSCI 4380', title: 'DevOps' },
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
      { code: 'CSCI 4620', title: 'Distributed Computing' },
    ],

    // ---- STEM & Ethics ----
    Stem_MathCore: [
      { code: 'MATH 1510', title: 'Calculus I' },
      { code: 'MATH 1520', title: 'Calculus II' },
      { code: 'MATH 1660', title: 'Discrete Mathematics' },
      { code: 'STAT 3850', title: 'Foundation of Statistics' },
    ],
    Stem_MathAdv: [
      { code: 'MATH 2530', title: 'Calculus III (example advanced math)' },
      { code: 'MATH 3110', title: 'Linear Algebra (example)' },
      { code: 'MATH 3120', title: 'Advanced Linear Algebra (example)' },
      { code: 'STAT 4000', title: 'Advanced Statistics (example)' },
      { code: 'MATH 3730', title: 'Numerical Methods (example)' },
      { code: 'MATH 4100', title: 'Advanced Topics in Math (example)' },
      { code: 'STAT 4100', title: 'Applied Statistics (example)' },
      { code: 'STAT 4200', title: 'Probability and Statistics (example)' },
    ],
    Stem_Science: [
      { code: 'PHYS 1310', title: 'Physics I with Lab (example)' },
      { code: 'PHYS 1320', title: 'Physics II with Lab (example)' },
      { code: 'CHEM 1110', title: 'General Chemistry I with Lab (example)' },
      { code: 'CHEM 1120', title: 'General Chemistry II with Lab (example)' },
      { code: 'BIOL 1240', title: 'Principles of Biology I with Lab (example)' },
      { code: 'BME 2000', title: 'Biomedical Engineering Computing' },
      { code: 'CVNG 1500', title: 'Civil Engineering Computing' },
      { code: 'SCI 2000', title: 'Science/Engineering Elective (example)' },
    ],
    Stem_Ethics: [
      { code: 'PHIL 3050X', title: 'Computer Ethics' },
      { code: 'CSCI 3050', title: 'Computer Ethics (CSCI listing)' },
      { code: 'PHIL 2050', title: 'Ethics (example prerequisite)' },
      { code: 'PHIL 3000', title: 'Advanced Ethics & Technology (example)' },
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
      { code: 'CSCI 4870', title: 'Applied Cryptography' },
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
      { code: 'CSCI 4845', title: 'Natural Language Processing' },
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
      { code: 'CSCI 4860', title: 'Autonomous Driving' },
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
      { code: 'CSCI 3980', title: 'Independent Study (Upper Division)' },
    ],
  };

  const createCourseCard = (course) => {
    const card = document.createElement('div');
    card.className = 'course-card p-4 rounded-xl relative cursor-pointer';

    const header = document.createElement('div');
    header.className = 'pr-10';

    const titleEl = document.createElement('p');
    titleEl.className = 'font-semibold mb-1';
    titleEl.textContent = `${course.code} – ${course.title}`;
    header.appendChild(titleEl);

    const desc = document.createElement('p');
    desc.className = 'mt-2 text-sm text-[#003DA5]/80 hidden';
    desc.textContent = 'Course details coming soon.';
    desc.dataset.role = 'description';

    const addBtn = document.createElement('button');
    addBtn.type = 'button';
    addBtn.className =
      'add-course-btn absolute top-2 right-2 text-xs px-2 py-1 rounded-full bg-[#53C3EE] text-[#003DA5] font-semibold shadow';
    addBtn.textContent = '+ Add';
    addBtn.setAttribute('data-code', course.code);
    addBtn.setAttribute('data-title', course.title);

    if (savedCourses.has(course.code)) {
      setButtonAddedState(addBtn);
    }

    card.addEventListener('click', (e) => {
      if (e.target === addBtn) return; 
      desc.classList.toggle('hidden');
    });

    addBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const code = addBtn.getAttribute('data-code');
      const title = addBtn.getAttribute('data-title');
      if (!code || !title) return;

      if (!savedCourses.has(code)) {
        savedCourses.set(code, { code, title });
      }
      renderSavedCourses();
      setButtonAddedState(addBtn);
    });

    card.appendChild(header);
    card.appendChild(desc);
    card.appendChild(addBtn);

    return card;
  };

  const displayCourses = (key) => {
    const courses = COURSE_DATA[key];
    if (!courses || courses.length === 0) {
      cardContainer.innerHTML =
        '<p class="text-center text-lg text-red-600 p-10">No courses found for this group.</p>';
      initialMessage?.classList.add('hidden');
      cardContainer.classList.remove('hidden');
      return;
    }

    cardContainer.innerHTML = '';
    courses.forEach((course) => {
      const card = createCourseCard(course);
      cardContainer.appendChild(card);
    });

    initialMessage?.classList.add('hidden');
    cardContainer.classList.remove('hidden');

    markButtonsForSavedCourses();

    document.getElementById('content-display')?.scrollIntoView({ behavior: 'smooth' });
  };

  buttons.forEach((button) => {
    button.addEventListener('click', (event) => {
      const targetKey = event.currentTarget.getAttribute('data-target');
      if (!targetKey) return;

      buttons.forEach((btn) => btn.classList.remove('ring-4', 'ring-accent', 'ring-opacity-50'));

      event.currentTarget.classList.add('ring-4', 'ring-accent', 'ring-opacity-50');

      displayCourses(targetKey);
    });
  });

  renderSavedCourses();
});
