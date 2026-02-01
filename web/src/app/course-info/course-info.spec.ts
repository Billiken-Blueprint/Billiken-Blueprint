import { TestBed } from '@angular/core/testing';
import { CourseInfoPage } from './course-info';

describe('CourseInfoPage', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CourseInfoPage],
    })
      .overrideComponent(CourseInfoPage, {
        set: { template: '<div>test host</div>' },
      })
      .compileComponents();
  });

  function setup() {
    const fixture = TestBed.createComponent(CourseInfoPage);
    const component = fixture.componentInstance;
    fixture.detectChanges();
    return { fixture, component };
  }

  it('should create', () => {
    const { component } = setup();
    expect(component).toBeTruthy();
  });

  it('should initialize with a non-empty courses list', () => {
    const { component } = setup();
    const list = component.courses();
    expect(Array.isArray(list)).toBeTrue();
    expect(list.length).toBeGreaterThan(0);
  });

  it('should include CSCI 1300 with multiple instructors and ratings preserved', () => {
    const { component } = setup();
    const cs1300 = component.courses().find(c => c.code === 'CSCI 1300');
    expect(cs1300).toBeTruthy();
    expect(cs1300!.instructors?.length).toBeGreaterThanOrEqual(2);

    // spot-check rating structure for first instructor
    const [i0] = cs1300!.instructors!;
    expect(i0.rating).toBeDefined();
    expect(typeof i0.rating!.overall).toBe('number');
    expect(typeof i0.rating!.numRatings).toBe('number');
  });

  it('toggleDesc should flip only the targeted course and keep immutability', () => {
    const { component } = setup();
    const before = component.courses();
    const prevRef = before;

    // pick an index that exists
    const idx = 0;
    expect(before[idx].expandedDesc).toBeFalse();

    component.toggleDesc(idx);
    const after = component.courses();

    // signal should emit a new array (immutability)
    expect(after).not.toBe(prevRef);

    // targeted item flips
    expect(after[idx].expandedDesc).toBeTrue();

    // non-targeted items remain the same
    for (let j = 0; j < after.length; j++) {
      if (j === idx) continue;
      expect(after[j].expandedDesc).toBeFalse();
    }

    // flip back
    component.toggleDesc(idx);
    const after2 = component.courses();
    expect(after2[idx].expandedDesc).toBeFalse();
  });

  it('toggleInstructors should flip only the targeted course and keep immutability', () => {
    const { component } = setup();
    const before = component.courses();
    const prevRef = before;

    const idx = 1; // a different course index for variety
    expect(before[idx].expandedInstructors).toBeFalse();

    component.toggleInstructors(idx);
    const after = component.courses();

    // new reference
    expect(after).not.toBe(prevRef);

    // only targeted item flips
    expect(after[idx].expandedInstructors).toBeTrue();
    for (let j = 0; j < after.length; j++) {
      if (j === idx) continue;
      expect(after[j].expandedInstructors).toBeFalse();
    }
  });

  it('should not mutate unrelated course objects when toggling', () => {
    const { component } = setup();

    // capture object references before toggle
    const before = component.courses();
    const refsBefore = before.map(c => c);

    component.toggleDesc(2);
    const after = component.courses();

    // the toggled index should be a different object reference
    expect(after[2]).not.toBe(refsBefore[2]);

    // other indices should retain their object references
    for (let j = 0; j < after.length; j++) {
      if (j === 2) continue;
      expect(after[j]).toBe(refsBefore[j]);
    }
  });

  it('courses signal should reflect consistent prerequisite and meeting fields when present', () => {
    const { component } = setup();
    const hasPrereq = component.courses().filter(c => !!c.prerequisites);
    // Just ensure the field exists and is a string when provided
    hasPrereq.forEach(c => {
      expect(typeof c.prerequisites).toBe('string');
    });

    const hasMeetingTimes = component.courses().filter(c => !!c.meetingTimes);
    hasMeetingTimes.forEach(c => {
      expect(typeof c.meetingTimes).toBe('string');
    });
  });
});

